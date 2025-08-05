"""
Tests for RLlib models.
"""

import pytest
import tensorflow as tf
import numpy as np
from gymnasium import spaces

from assembly_line_system.rllib_models.conveyor_model import ConveyorModel

def test_conveyor_model_initialization():
    """Test that the conveyor model initializes correctly."""
    # Create mock spaces
    obs_space = spaces.Box(low=0, high=1, shape=(6, 3), dtype=np.float32)
    action_space = spaces.Discrete(4)

    # Create model
    model = ConveyorModel(
        obs_space=obs_space,
        action_space=action_space,
        num_outputs=4,
        model_config={},
        name="conveyor_model"
    )

    # Check that the model has the expected layers
    assert len(model.shared_layers.layers) == 2
    assert len(model.conveyor_layers.layers) == 2

def test_conveyor_model_forward_pass():
    """Test the forward pass through the conveyor model."""
    # Create mock spaces
    obs_space = spaces.Box(low=0, high=1, shape=(6, 3), dtype=np.float32)
    action_space = spaces.Discrete(4)

    # Create model
    model = ConveyorModel(
        obs_space=obs_space,
        action_space=action_space,
        num_outputs=4,
        model_config={},
        name="conveyor_model"
    )

    # Create dummy input (np already imported at top)
    obs = np.random.rand(6, 3).astype(np.float32)
    input_dict = {"obs": tf.convert_to_tensor(obs)}

    # Run forward pass
    logits, state = model.forward(input_dict, [], None)

    # Check outputs - note: shape should be [batch_size, num_outputs]
    assert logits.shape[1] == 4  # Second dimension should be num_outputs
    assert len(state) == 0  # No RNN state for this model, so should be empty list

def test_conveyor_model_value_function():
    """Test the value function of the conveyor model."""
    # Create mock spaces
    obs_space = spaces.Box(low=0, high=1, shape=(6, 3), dtype=np.float32)
    action_space = spaces.Discrete(4)

    # Create model
    model = ConveyorModel(
        obs_space=obs_space,
        action_space=action_space,
        num_outputs=4,
        model_config={},
        name="conveyor_model"
    )

    # Create dummy input (np already imported at top)
    obs = np.random.rand(6, 3).astype(np.float32)
    model.inputs = tf.convert_to_tensor(obs)

    # Run value function
    value = model.value_function()

    # Check output - note: shape should be [batch_size, num_outputs]
    assert value.shape[1] == 4  # Second dimension should be num_outputs

def test_conveyor_model_training():
    """Test that the conveyor model can be trained."""
    # Create mock spaces
    obs_space = spaces.Box(low=0, high=1, shape=(6, 3), dtype=np.float32)
    action_space = spaces.Discrete(4)

    # Create model
    model = ConveyorModel(
        obs_space=obs_space,
        action_space=action_space,
        num_outputs=4,
        model_config={},
        name="conveyor_model"
    )

    # Create dummy input and target (np already imported at top)
    obs = np.random.rand(32, 6, 3).astype(np.float32)  # Batch of 32
    actions = np.random.randint(0, 4, size=(32,))
    rewards = np.random.rand(32).astype(np.float32)

    # Convert to tensors
    obs_tensor = tf.convert_to_tensor(obs)
    actions_one_hot = tf.one_hot(actions, 4)
    rewards_tensor = tf.convert_to_tensor(rewards)

    # Define loss function
    def loss_fn():
        logits, _ = model.forward({"obs": obs_tensor}, [], None)
        # Reshape to match target shape: actions has shape (32,), so we need logits with shape (32, 4)
        # The model outputs shape (32, 6, 4), so we need to reshape to (32*6, 4) then slice
        logits_reshaped = tf.reshape(logits, [-1, 4])[:32]
        loss = tf.keras.losses.sparse_categorical_crossentropy(
            actions, logits_reshaped, from_logits=True
        )
        return tf.reduce_mean(loss)

    # Create optimizer and train step
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

    @tf.function
    def train_step():
        with tf.GradientTape() as tape:
            loss = loss_fn()
        # Get trainable variables from the model's shared and conveyor layers
        trainable_vars = []
        for layer in model.shared_layers.layers:
            if hasattr(layer, 'trainable_variables'):
                trainable_vars.extend(layer.trainable_variables)
        for layer in model.conveyor_layers.layers:
            if hasattr(layer, 'trainable_variables'):
                trainable_vars.extend(layer.trainable_variables)

        gradients = tape.gradient(loss, trainable_vars)
        optimizer.apply_gradients(zip(gradients, trainable_vars))
        return loss

    # Run a few training steps
    for _ in range(3):
        loss = train_step()
        assert loss is not None