// Copyright (c) 2023 PaddlePaddle Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License"); you may
// not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
#include "kernels/funcs.h"
#include "kernels/hpu_operator.h"
#include "utils/utils.h"

namespace custom_kernel {

class GatherND : public HpuOperator {
 public:
  GatherND() : HpuOperator("gather_nd_fwd_") {}

  void AddNode(ConvertTensors &ct) {
    auto inputs = ct.GetTensors();
    auto outputs = ct.GetTensors(false);

    std::vector<synTensor> syn_inputs;
    for (size_t i = 0; i < inputs.size(); i++) {
      syn_inputs.push_back(createTensor(inputs[i].dims.size(),
                                        inputs[i].type,
                                        inputs[i].dims,
                                        true,
                                        inputs[i].name));
    }

    std::vector<synTensor> syn_outputs;
    for (size_t i = 0; i < outputs.size(); i++) {
      syn_outputs.push_back(createTensor(outputs[i].dims.size(),
                                         outputs[i].type,
                                         outputs[i].dims,
                                         true,
                                         outputs[i].name));
    }

    guid_ = guid_ + SynDataTypeToStr(inputs[0].type);

    synStatus status = synNodeCreate(graphHandle_,
                                     syn_inputs.data(),
                                     syn_outputs.data(),
                                     syn_inputs.size(),
                                     syn_outputs.size(),
                                     nullptr,
                                     0,
                                     guid_.c_str(),
                                     "gather",
                                     nullptr,
                                     nullptr);
    PD_CHECK(
        status == synSuccess, "[RUNTIME] synNodeCreate () failed = %d", status);
  }
};

template <typename T, typename Context>
void GatherNdKernel(const Context &dev_ctx,
                    const phi::DenseTensor &x,
                    const phi::DenseTensor &index,
                    phi::DenseTensor *out) {
  dev_ctx.template Alloc<T>(out);

  if (x.numel() == 0) {
    return;
  }

  ConvertTensors ct;
  ct.Add(x);
  ct.Add(index);
  ct.Add(out, false);

  std::vector<DIMS> inputs_dims = ct.GetDims();
  OpCacheOperator op_info;
  op_info.prepareOpInfo<T, nullptr_t>("GatherNdKernel", inputs_dims, nullptr);
  auto recipe = op_info.GetRecipe();

  if (recipe == nullptr) {
    GatherND op;
    op.AddNode(ct);
    op.Compile();
    op_info.setOp(op);
    recipe = op_info.GetRecipe();
  }

  RecipeRunner runner(recipe);
  auto tensors = ct.GetDeviceAddr();
  runner.Run(reinterpret_cast<C_Stream>(dev_ctx.stream()), tensors);
}

}  // namespace custom_kernel

PD_REGISTER_PLUGIN_KERNEL(gather_nd,
                          intel_hpu,
                          ALL_LAYOUT,
                          custom_kernel::GatherNdKernel,
                          int,
                          phi::dtype::float16,
                          phi::dtype::bfloat16,
                          float,
                          bool) {}
