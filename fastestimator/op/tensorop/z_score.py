# Copyright 2019 The FastEstimator Authors. All Rights Reserved.
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
# ==============================================================================
import tensorflow as tf

from fastestimator.op import TensorOp

EPSILON = 1e-7


class Zscore(TensorOp):
    """Standardize data using zscore method.
    """
    def forward(self, data, state):
        """Standardizes the data tensor.

        Args:
            data: Data to be standardized.
            state: Information about the current execution context.

        Returns:
            Tensor containing standardized data.
        """
        data = tf.cast(data, tf.float32)
        mean = tf.reduce_mean(data)
        std = tf.keras.backend.std(data)
        data = tf.math.divide(tf.subtract(data, mean), tf.maximum(std, EPSILON))
        data = tf.cast(data, tf.float32)

        return data
