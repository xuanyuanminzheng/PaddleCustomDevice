// Copyright (c) 2024 PaddlePaddle Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#pragma once
#ifdef PADDLE_WITH_ATB

#include "atb/atb_infer.h"

namespace atb_layers {

struct QKVSplitParam {
  int64_t head_num;
  int64_t kv_head_num{0};
  int64_t head_dim;
};

void CreateQKVSplit(const QKVSplitParam& param, atb::Operation** operation);

}  // namespace atb_layers

namespace atb {
template <>
inline Status CreateOperation(const atb_layers::QKVSplitParam& opParam,
                              Operation** operation) {
  atb_layers::CreateQKVSplit(opParam, operation);
  return ErrorType::NO_ERROR;
}
}  // namespace atb

#endif
