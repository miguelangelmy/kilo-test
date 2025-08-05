"""
RLlib model for Assembly Station Agent.
"""

from ray.rllib.models.tf.tf_modelv2 import TFModelV2
import tensorflow as tf

class AssemblyStationModel(TFModelV2):
    """
    Custom RLlib model for assembly station agents.

    This model extends the base TFModelV2 to provide specialized
    neural network architecture for assembly station decision making,
    including quality control and production optimization.
    """

    def __init__(self, obs_space, action_space, num_outputs, model_config, name):
        """
        Initialize the assembly station model.

        Args:
            obs_space: Observation space
            action_space: Action space
            num_outputs: Number of output nodes
            model_config: Model configuration
            name: Name of the model
        """
        super(AssemblyStationModel, self).__init__(obs_space, action_space, num_outputs, model_config, name)

        # Define shared layers for feature extraction
        self.shared_layers = tf.keras.Sequential([
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.1),  # Low dropout for critical assembly tasks
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dense(64, activation='relu')
        ])

        # Value function layers (separate from action logits)
        self.value_layers = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1)  # Single value output
        ])

        # Action logits layers for assembly station operations
        self.action_layers = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.BatchNormalization(),
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

        # Cache the shared output for value function computation
        self._last_shared_out = shared_out

        # Compute action logits
        logits = self.action_layers(shared_out)

        return logits, state

    def value_function(self):
        """
        Compute the value function.

        Returns:
            Value tensor
        """
        # Use cached shared output from forward pass or compute from current observation
        if hasattr(self, '_last_shared_out'):
            # Use cached shared output from forward pass
            value_out = self.value_layers(self._last_shared_out)
        else:
            # Fallback: compute from current observation
            obs = self.get_current_observation()
            shared_out = self.shared_layers(obs)
            value_out = self.value_layers(shared_out)
        
        return tf.reshape(value_out, [-1])

    def get_current_observation(self):
        """
        Get current observation for value function computation.
        
        Returns:
            Current observation tensor
        """
        # This method should be implemented based on how observations are provided
        # For now, return a placeholder that will be overridden by actual usage
        if hasattr(self, '_last_obs'):
            return self._last_obs
        else:
            # Return a dummy tensor of appropriate shape
            obs_shape = self.observation_space.shape
            return tf.zeros((1,) + obs_shape, dtype=tf.float32)