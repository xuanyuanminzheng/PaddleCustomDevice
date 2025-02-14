#   Copyright (c) 2018 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import unittest
import numpy as np
from op_test import OpTest
import paddle.base as base
import paddle

paddle.enable_static()


def get_places(self):
    return [paddle.CustomPlace("intel_gpu", 0)]


OpTest._get_places = get_places


# Situation 1: starts(list, no tensor), ends(list, no tensor)
# 1.1 without attr(decrease)
class TestSliceOp(OpTest):
    def setUp(self):
        self.op_type = "slice"
        self.config()
        self.inputs = {"Input": self.input}
        self.outputs = {"Out": self.out}
        self.attrs = {
            "axes": self.axes,
            "starts": self.starts,
            "ends": self.ends,
            "infer_flags": self.infer_flags,
        }

    def config(self):
        self.input = np.random.random([3, 4, 5, 6]).astype("float64")
        self.starts = [1, 0, 2]
        self.ends = [3, 3, 4]
        self.axes = [0, 1, 2]
        self.infer_flags = [1, 1, 1]
        self.out = self.input[1:3, 0:3, 2:4, :]

    def test_check_output(self):
        self.check_output()

    def test_check_grad_normal(self):
        self.check_grad(["Input"], "Out", max_relative_error=0.006)


class TestCase1(TestSliceOp):
    def config(self):
        self.input = np.random.random([3, 4, 5, 6]).astype("float64")
        self.starts = [-3, 0, 2]
        self.ends = [3, 100, -1]
        self.axes = [0, 1, 2]
        self.infer_flags = [1, 1, 1]
        self.out = self.input[-3:3, 0:100, 2:-1, :]


class TestCase2(TestSliceOp):
    def config(self):
        self.input = np.random.random([3, 4, 5, 6]).astype("float64")
        self.starts = [-3, 0, 2]
        self.ends = [3, 100, -1]
        self.axes = [0, 1, 3]
        self.infer_flags = [1, 1, 1]
        self.out = self.input[-3:3, 0:100, :, 2:-1]


# 1.2 with attr(decrease)
class TestSliceOp_decs_dim(OpTest):
    def setUp(self):
        self.op_type = "slice"
        self.config()
        self.inputs = {"Input": self.input}
        self.outputs = {"Out": self.out}
        self.attrs = {
            "axes": self.axes,
            "starts": self.starts,
            "ends": self.ends,
            "infer_flags": self.infer_flags,
            "decrease_axis": self.decrease_axis,
        }

    def config(self):
        self.input = np.random.random([3, 4, 5, 6]).astype("float64")
        self.starts = [1, 0, 2]
        self.ends = [2, 3, 4]
        self.axes = [0, 1, 2]
        self.decrease_axis = [0]
        self.infer_flags = [1, 1, 1]
        self.out = self.input[1, 0:3, 2:4, :]

    def test_check_output(self):
        self.check_output()

    def test_check_grad_normal(self):
        self.check_grad(["Input"], "Out", max_relative_error=0.006)


class TestSliceOp_decs_dim_2(TestSliceOp_decs_dim):
    def config(self):
        self.input = np.random.random([3, 4, 5, 6]).astype("float64")
        self.starts = [1, 0, 2]
        self.ends = [2, 1, 4]
        self.axes = [0, 1, 2]
        self.decrease_axis = [0, 1]
        self.infer_flags = [1, 1, 1]
        self.out = self.input[1, 0, 2:4, :]


class TestSliceOp_decs_dim_3(TestSliceOp_decs_dim):
    def config(self):
        self.input = np.random.random([3, 4, 5, 6]).astype("float64")
        self.starts = [-1, 0, 2]
        self.ends = [1000000, 1, 4]
        self.axes = [0, 1, 2]
        self.decrease_axis = [0, 1]
        self.infer_flags = [1, 1, 1]
        self.out = self.input[-1, 0, 2:4, :]


class TestSliceOp_decs_dim_4(TestSliceOp_decs_dim):
    def config(self):
        self.input = np.random.random([3, 4, 5, 7]).astype("float64")
        self.starts = [0, 1, 2, 3]
        self.ends = [1, 2, 3, 4]
        self.axes = [0, 1, 2, 3]
        self.decrease_axis = [0, 1, 2, 3]
        self.infer_flags = [1, 1, 1]
        self.out = self.input[0, 1, 2, 3:4]


class TestSliceOp_decs_dim_5(TestSliceOp_decs_dim):
    def config(self):
        self.input = np.random.random([3, 4, 5, 6]).astype("float64")
        self.starts = [-1]
        self.ends = [1000000]
        self.axes = [3]
        self.decrease_axis = [3]
        self.infer_flags = [1, 1, 1]
        self.out = self.input[:, :, :, -1]


class TestSliceOp_decs_dim_6(TestSliceOp_decs_dim):
    def config(self):
        self.input = np.random.random([3, 4, 5, 6]).astype("float64")
        self.starts = [0, 1, 2, 3]
        self.ends = [1, 2, 3, 4]
        self.axes = [0, 1, 2, 3]
        self.decrease_axis = [0, 1, 2, 3]
        self.infer_flags = [1, 1, 1]
        self.out = self.input[0, 1, 2, 3:4]


# Situation 2: starts(list, have tensor), ends(list, no tensor)
# without attr(decrease)
class TestSliceOp_starts_ListTensor(OpTest):
    def setUp(self):
        self.op_type = "slice"
        self.config()

        starts_tensor = []
        for index, ele in enumerate(self.starts):
            starts_tensor.append(("x" + str(index), np.ones((1)).astype("int64") * ele))

        self.inputs = {"Input": self.input, "StartsTensorList": starts_tensor}
        self.outputs = {"Out": self.out}
        self.attrs = {
            "axes": self.axes,
            "starts": self.starts_infer,
            "ends": self.ends,
            "infer_flags": self.infer_flags,
        }

    def config(self):
        self.input = np.random.random([3, 4, 5, 6]).astype("float64")
        self.starts = [1, 0, 2]
        self.ends = [3, 3, 4]
        self.axes = [0, 1, 2]
        self.infer_flags = [-1, 1, -1]
        self.out = self.input[1:3, 0:3, 2:4, :]

        self.starts_infer = [-1, 0, -1]

    def test_check_output(self):
        self.check_output()

    def test_check_grad_normal(self):
        self.check_grad(["Input"], "Out", max_relative_error=0.006)


# Situation 2: starts(list, have tensor), ends(list, no tensor)
#  with attr(decrease)
class TestSliceOp_decs_dim_starts_ListTensor(OpTest):
    def setUp(self):
        self.op_type = "slice"
        self.config()

        starts_tensor = []
        for index, ele in enumerate(self.starts):
            starts_tensor.append(("x" + str(index), np.ones((1)).astype("int32") * ele))

        self.inputs = {"Input": self.input, "StartsTensorList": starts_tensor}

        self.outputs = {"Out": self.out}
        self.attrs = {
            "axes": self.axes,
            "starts": self.starts_infer,
            "ends": self.ends,
            "infer_flags": self.infer_flags,
            "decrease_axis": self.decrease_axis,
        }

    def config(self):
        self.input = np.random.random([3, 4, 5, 6]).astype("float64")
        self.starts = [1, 0, 2]
        self.ends = [2, 3, 4]
        self.axes = [0, 1, 2]
        self.decrease_axis = [0]
        self.infer_flags = [1, -1, 1]
        self.out = self.input[1, 0:3, 2:4, :]

        self.starts_infer = [1, -1, 2]

    def test_check_output(self):
        self.check_output()

    def test_check_grad_normal(self):
        self.check_grad(["Input"], "Out", max_relative_error=0.006)


class TestSliceOp_decs_dim_5_starts_ListTensor(TestSliceOp_decs_dim_starts_ListTensor):
    def config(self):
        self.input = np.random.random([3, 4, 5, 6]).astype("float64")
        self.starts = [-1]
        self.ends = [1000000]
        self.axes = [3]
        self.decrease_axis = [3]
        self.infer_flags = [-1]
        self.out = self.input[:, :, :, -1]

        self.starts_infer = [-1]


# Situation 3: starts(tensor), ends(list, no tensor)
# with attr(decrease)
class TestSliceOp_decs_dim_starts_OneTensor(OpTest):
    def setUp(self):
        self.op_type = "slice"
        self.config()
        self.inputs = {
            "Input": self.input,
            "StartsTensor": np.array(self.starts, dtype="int32"),
        }
        self.outputs = {"Out": self.out}
        self.attrs = {
            "axes": self.axes,
            "ends": self.ends,
            "infer_flags": self.infer_flags,
            "decrease_axis": self.decrease_axis,
        }

    def config(self):
        self.input = np.random.random([3, 4, 5, 6]).astype("float64")
        self.starts = [1, 0, 2]
        self.ends = [2, 3, 4]
        self.axes = [0, 1, 2]
        self.decrease_axis = [0]
        self.infer_flags = [-1, -1, -1]
        self.out = self.input[1, 0:3, 2:4, :]

    def test_check_output(self):
        self.check_output()

    def test_check_grad_normal(self):
        self.check_grad(["Input"], "Out", max_relative_error=0.006)


# Situation 4: starts(tensor), ends(tensor)
#  without attr(decrease)
class TestSliceOp_starts_OneTensor_ends_OneTensor(OpTest):
    def setUp(self):
        self.op_type = "slice"
        self.config()

        self.inputs = {
            "Input": self.input,
            "StartsTensor": np.array(self.starts, dtype="int64"),
            "EndsTensor": np.array(self.ends, dtype="int32"),
        }
        self.outputs = {"Out": self.out}
        self.attrs = {
            "axes": self.axes,
            "infer_flags": self.infer_flags,
        }

    def config(self):
        self.input = np.random.random([3, 4, 5, 6]).astype("float64")
        self.starts = [1, 0, 2]
        self.ends = [3, 3, 4]
        self.axes = [0, 1, 2]
        self.infer_flags = [-1, -1, -1]
        self.out = self.input[1:3, 0:3, 2:4, :]

    def test_check_output(self):
        self.check_output()

    def test_check_grad_normal(self):
        self.check_grad(["Input"], "Out", max_relative_error=0.006)


# Situation 5: starts(tensor), ends(tensor)
#  with attr(decrease)
class TestSliceOp_decs_dim_starts_and_ends_OneTensor(OpTest):
    def setUp(self):
        self.op_type = "slice"
        self.config()
        self.inputs = {
            "Input": self.input,
            "StartsTensor": np.array(self.starts, dtype="int32"),
            "EndsTensor": np.array(self.ends, dtype="int32"),
        }
        self.outputs = {"Out": self.out}
        self.attrs = {
            "axes": self.axes,
            "infer_flags": self.infer_flags,
            "decrease_axis": self.decrease_axis,
        }

    def config(self):
        self.input = np.random.random([3, 4, 5, 6]).astype("float64")
        self.starts = [1, 0, 2]
        self.ends = [2, 1, 4]
        self.axes = [0, 1, 2]
        self.decrease_axis = [0, 1]
        self.infer_flags = [-1, -1, -1]
        self.out = self.input[1, 0, 2:4, :]

    def test_check_output(self):
        self.check_output()

    def test_check_grad_normal(self):
        self.check_grad(["Input"], "Out", max_relative_error=0.006)


# Situation 6: starts(tensor), ends(list, have tensor)
# without attr(decrease)
class TestSliceOp_starts_OneTensor_ends_ListTensor(OpTest):
    def setUp(self):
        self.op_type = "slice"
        self.config()

        ends_tensor = []
        for index, ele in enumerate(self.ends):
            ends_tensor.append(("y" + str(index), np.ones((1)).astype("int32") * ele))

        self.inputs = {
            "Input": self.input,
            "StartsTensor": np.array(self.starts, dtype="int32"),
            "EndsTensorList": ends_tensor,
        }
        self.outputs = {"Out": self.out}
        self.attrs = {
            "axes": self.axes,
            "ends": self.ends_infer,
            "infer_flags": self.infer_flags,
        }

    def config(self):
        self.input = np.random.random([3, 4, 5, 6]).astype("float64")
        self.starts = [1, 0, 2]
        self.ends = [3, 3, 4]
        self.axes = [0, 1, 2]
        self.infer_flags = [-1, -1, -1]
        self.out = self.input[1:3, 0:3, 2:4, :]

        self.ends_infer = [-1, 3, 4]

    def test_check_output(self):
        self.check_output()

    def test_check_grad_normal(self):
        self.check_grad(["Input"], "Out", max_relative_error=0.006)


# Test python API
class TestSliceAPI(unittest.TestCase):
    def test_1(self):
        input = np.random.random([3, 4, 5, 6]).astype("float64")
        minus_1 = base.layers.fill_constant([1], "int32", -1)
        minus_3 = base.layers.fill_constant([1], "int64", -3)
        starts = base.layers.data(name="starts", shape=[1, 3], append_batch_size=False)
        ends = base.layers.data(name="ends", shape=[3], append_batch_size=False)

        x = base.layers.data(
            name="x", shape=[3, 4, 5, 6], append_batch_size=False, dtype="float64"
        )

        # value_int64 is greater than 2147483647 which is the max of int32
        value_int64 = base.layers.fill_constant([1], "int64", 2147483648)

        out_1 = paddle.slice(
            x, axes=[0, 1, 2], starts=[-3, 0, 2], ends=[value_int64, 100, -1]
        )
        out_2 = paddle.slice(
            x, axes=[0, 1, 3], starts=[minus_3, 0, 2], ends=[3, 100, -1]
        )
        out_3 = paddle.slice(
            x, axes=[0, 1, 3], starts=[minus_3, 0, 2], ends=[3, 100, minus_1]
        )
        out_4 = paddle.slice(x, axes=[0, 1, 2], starts=starts, ends=ends)

        out_5 = x[-3:3, 0:100, 2:-1]
        out_6 = x[minus_3:3, 0:100, :, 2:-1]
        out_7 = x[minus_1, 0:100, :, 2:minus_1]

        exe = base.Executor(place=base.CustomPlace("intel_gpu", 0))
        res_1, res_2, res_3, res_4, res_5, res_6, res_7 = exe.run(
            base.default_main_program(),
            feed={
                "x": input,
                "starts": np.array([-3, 0, 2]).astype("int32"),
                "ends": np.array([3, 100, -1]).astype("int32"),
            },
            fetch_list=[out_1, out_2, out_3, out_4, out_5, out_6, out_7],
        )

        assert np.array_equal(res_1, input[-3:3, 0:100, 2:-1, :])
        assert np.array_equal(res_2, input[-3:3, 0:100, :, 2:-1])
        assert np.array_equal(res_3, input[-3:3, 0:100, :, 2:-1])
        assert np.array_equal(res_4, input[-3:3, 0:100, 2:-1, :])
        assert np.array_equal(res_5, input[-3:3, 0:100, 2:-1, :])
        assert np.array_equal(res_6, input[-3:3, 0:100, :, 2:-1])
        assert np.array_equal(res_7, input[-1, 0:100, :, 2:-1])


class TestSliceApiWithTensor(unittest.TestCase):
    def test_starts_ends_is_tensor(self):
        with paddle.base.dygraph.guard(paddle.CustomPlace("intel_gpu", 0)):
            a = paddle.rand(shape=[4, 5, 6], dtype="float32")
            axes = [0, 1, 2]
            starts = [-3, 0, 2]
            ends = [3, 2, 4]
            a_1 = paddle.slice(
                a,
                axes=axes,
                starts=paddle.to_tensor(starts, dtype="int32"),
                ends=paddle.to_tensor(ends, dtype="int32"),
            )
            a_2 = paddle.slice(a, axes=axes, starts=starts, ends=ends)

            self.assertTrue(np.array_equal(a_1.numpy(), a_2.numpy()))

    def test_bool_tensor(self):
        with paddle.base.dygraph.guard(paddle.CustomPlace("intel_gpu", 0)):
            array = (np.arange(60).reshape([3, 4, 5]) % 3).astype("bool")
            tt = paddle.to_tensor(array)
            tt.stop_gradient = False

            starts = [0, 1, 2]
            ends = [3, 5, 4]
            axes = [0, 1, 2]

            y_paddle = paddle.slice(tt, axes, starts, ends)
            y_np = tt[0:3, 1:5, 2:4]

            self.assertTrue(paddle.bool == y_paddle.dtype)
            self.assertTrue(np.array_equal(y_paddle.numpy(), y_np))


# unknown bug (wangran16)


class TestSliceApiEager(unittest.TestCase):
    def test_slice_api(self):
        with paddle.base.dygraph.guard(paddle.CustomPlace("intel_gpu", 0)):
            a = paddle.rand(shape=[4, 5, 6], dtype="float32")
            a.stop_gradient = False
            axes = [0, 1, 2]
            starts = [-3, 0, 2]
            ends = [3, 2, 4]
            a_1 = paddle.slice(a, axes=axes, starts=starts, ends=ends)

            a_2 = paddle.slice(
                a,
                axes=axes,
                starts=paddle.to_tensor(starts),
                ends=paddle.to_tensor(ends),
            )

            a_1.backward()
            grad_truth = paddle.zeros_like(a)
            grad_truth[-3:3, 0:2, 2:4] = 1
            self.assertTrue(np.array_equal(grad_truth, a.gradient()))

            self.assertTrue(np.allclose(a_1.numpy(), a[-3:3, 0:2, 2:4]))


# TODO(Zhiwei35): the case's expected dispatch to phi kernels, but base
# kernels, I think this is paddle bug?
# UnimplementedError: There are no kernels which are registered in the memcpy_d2h operator.
# [Hint: Expected kernels_iter != all_op_kernels.end(), but received
# kernels_iter == all_op_kernels.end().] (at /home/gta/chaofanl/PaddleIntelGPUDevice/
# Paddle/paddle/base/framework/operator.cc:1893)
# [operator < slice > error]
# class TestSliceApiWithDenseTensorArray(unittest.TestCase):
#     def setUp(self):
#         self.shape = (3, 4)
#         self.data = np.random.random(size=self.shape).astype('float32')
#         self.idx = 0
#         self.start = 0
#         self.end = 2
#         self.axis = 1

#         self.place = base.CustomPlace(
#             'intel_gpu',
#             0) if base.is_compiled_with_cuda() else base.CustomPlace(
#                 'intel_gpu', 0)
#         self.exe = base.Executor(self.place)

#     def set_program_and_run(self, main_program, case_num):
#         with base.program_guard(main_program):
#             x = [
#                 base.data(
#                     name='x0', shape=self.shape, dtype="float32"), base.data(
#                         name='x1', shape=self.shape, dtype="float32"),
#                 base.data(
#                     name='x2', shape=self.shape, dtype="float32")
#             ]

#             for each_x in x:
#                 each_x.stop_gradient = False

#             arr = layers.create_array(dtype="float32")
#             for i in range(3):
#                 idx = layers.array_length(arr)
#                 arr = layers.array_write(x=x[i], i=idx, array=arr)

#             if case_num == 1:
#                 self.sliced_arr = output = arr[0]

#             elif case_num == 2:
#                 end = base.layers.array_length(
#                     arr) - 1  # dtype of end is int64
#                 self.sliced_arr = slice_arr = arr[self.start:end]
#                 output, _ = base.layers.tensor_array_to_tensor(
#                     slice_arr, axis=self.axis, use_stack=True)
#             elif case_num == 3:
#                 value_int64 = base.layers.fill_constant([1], "int64",
#                                                          2147483648)
#                 self.sliced_arr = slice_arr = arr[self.start:value_int64]
#                 output, _ = base.layers.tensor_array_to_tensor(
#                     slice_arr, axis=self.axis, use_stack=True)

#             loss = base.layers.reduce_sum(output)
#             base.backward.append_backward(loss)
#             g_vars = list(
#                 map(main_program.global_block().var,
#                     [each_x.name + "@GRAD" for each_x in x]))
#             self.out, self.g_x0, self.g_x1, self.g_x2 = \
#                 self.exe.run(main_program,
#                              feed = {'x0': self.data,
#                                      'x1': self.data,
#                                      'x2': self.data},
#                              fetch_list=[output] + g_vars)

#     def test_case_1(self):
#         main_program = base.Program()
#         self.set_program_and_run(main_program, 1)

#         self.assertTrue(self.sliced_arr.type == core.VarDesc.VarType.DENSE_TENSOR)
#         self.assertEqual(self.sliced_arr.shape, self.shape)
#         self.assertTrue(np.array_equal(self.out, self.data))
#         self.assertTrue(np.array_equal(self.g_x0, np.ones_like(self.data)))
#         self.assertTrue(np.array_equal(self.g_x1, np.zeros_like(self.data)))
#         self.assertTrue(np.array_equal(self.g_x2, np.zeros_like(self.data)))

#     def test_case_2(self):
#         main_program = base.Program()
#         self.set_program_and_run(main_program, 2)

#         self.assertTrue(
#             self.sliced_arr.type == core.VarDesc.VarType.DENSE_TENSOR_ARRAY)
#         self.assertEqual(self.sliced_arr.shape, self.shape)
#         self.assertTrue(
#             np.array_equal(
#                 self.out, np.stack(
#                     [self.data, self.data], axis=self.axis)))
#         self.assertTrue(np.array_equal(self.g_x0, np.ones_like(self.data)))
#         self.assertTrue(np.array_equal(self.g_x1, np.ones_like(self.data)))
#         self.assertTrue(np.array_equal(self.g_x2, np.zeros_like(self.data)))

#     def test_case_3(self):
#         main_program = base.Program()
#         self.set_program_and_run(main_program, 3)

#         self.assertTrue(
#             self.sliced_arr.type == core.VarDesc.VarType.DENSE_TENSOR_ARRAY)
#         self.assertEqual(self.sliced_arr.shape, self.shape)
#         self.assertTrue(
#             np.array_equal(
#                 self.out,
#                 np.stack(
#                     [self.data, self.data, self.data], axis=self.axis)))
#         self.assertTrue(np.array_equal(self.g_x0, np.ones_like(self.data)))
#         self.assertTrue(np.array_equal(self.g_x1, np.ones_like(self.data)))
#         self.assertTrue(np.array_equal(self.g_x2, np.ones_like(self.data)))


class TestImperativeVarBaseGetItem(unittest.TestCase):
    def test_getitem_with_long(self):
        with base.dygraph.guard(paddle.CustomPlace("intel_gpu", 0)):
            data = np.random.random((2, 80, 16128)).astype("float32")
            var = paddle.to_tensor(data)
            sliced = var[:, 10:, : var.shape[1]]  # var.shape[1] is 80L here
            self.assertEqual(sliced.shape, [2, 70, 80])

            sliced = var[:, var.shape[0] :, var.shape[0] : var.shape[1]]
            self.assertEqual(sliced.shape, [2, 78, 78])

    def test_getitem_with_float(self):
        def test_float_in_slice_item():
            with base.dygraph.guard(paddle.CustomPlace("intel_gpu", 0)):
                data = np.random.random((2, 80, 16128)).astype("float32")
                var = paddle.to_tensor(data)
                sliced = var[:, 1.1:, : var.shape[1]]

        self.assertRaises(Exception, test_float_in_slice_item)

        def test_float_in_index():
            with base.dygraph.guard(paddle.CustomPlace("intel_gpu", 0)):
                data = np.random.random((2, 80, 16128)).astype("float32")
                var = paddle.to_tensor(data)
                sliced = var[1.1]

        self.assertRaises(Exception, test_float_in_index)


if __name__ == "__main__":
    paddle.enable_static()
    unittest.main()
