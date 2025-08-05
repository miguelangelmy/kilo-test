"""
RLlib model for Conveyor Belt Agent.
"""

from ray.rllib.models.tf.tf_modelv2 import TFModelV2
import tensorflow as tf

class ConveyorModel(TFModelV2):
    """
    Custom RLlib model for conveyor belt agents.

    This model extends the base TFModelV2 to provide specialized
    neural network architecture for conveyor belt decision making.
    """

    def __init__(self, obs_space, action_space, num_outputs, model_config, name):
        """
        Initialize the conveyor model.

        Args:
            obs_space: Observation space
            action_space: Action space
            num_outputs: Number of output nodes
            model_config: Model configuration
            name: Name of the model
        """
        super(ConveyorModel, self).__init__(obs_space, action_space, num_outputs, model_config, name)

        # Define shared layers
        self.shared_layers = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(64, activation='relu')
        ])

        # Value function layers (separate from action logits)
        self.value_layers = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(1)  # Single value output
        ])

        # Action logits layers
        self.action_layers = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(num_outputs)  # Linear activation for logits
        ])

    def forward(self, input_dict, state, seq_lens):
        """
        Forward pass through the network.

        Args:
            input_dict: Input dictionary containing observations
            state: State of the RNN (if applicable)
            seq_lens: Sequence lengths for RNNs

        Returns:
            Output tensor and updated state
        """
        # Process observations through shared layers
        obs = input_dict["obs"]
        shared_out = self.shared_layers(obs)

        # Compute action logits
        logits = self.action_layers(shared_out)

        return logits, state

    def value_function(self):
        """
        Compute the value function.

        Returns:
            Value tensor
        """
        # Use the last layer input from forward pass or compute from current observation
        if hasattr(self, '_last_shared_out'):
            # Use cached shared output from forward pass
            value_out = self.value_layers(self._last_shared_out)
        else:
            # Fallback: compute from current observation
            obs = self.get_current_observation()
            shared_out = self.shared_layers(obs)
            value_out = self.value_layers(shared_out)
        
        return tf.reshape(value_out, [-1])