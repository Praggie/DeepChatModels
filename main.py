#!/usr/bin/env python3

"""main.py: Train and/or chat with a bot. (work in progress).

Typical use cases:
    1.  Train a model specified by yaml config file, located at
        path_to/my_config.yml, where paths are relative to project root:
            ./main.py --config path_to/my_config.yml

    2.  Train using mix of yaml config and cmd-line args, with
        command-line args taking precedence over any values.
            ./main.py \
                --config path_to/my_config.yml \
                --model_params "
                    batch_size: 32,
                    optimizer: RMSProp "

    3.  Load a pretrained model that was saved in path_to/pretrained_dir,
        which is assumed to be relative to the project root.
            ./main.py --pretrained_dir path_to/pretrained_dir

"""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='1'

import data
import chatbot
import tensorflow as tf
from pydoc import locate
from utils import io_utils

# Allow user to override config values with command-line args.
flags = tf.app.flags
flags.DEFINE_string("pretrained_dir", None, "path to pretrained model dir.")
flags.DEFINE_string("config", None, "path to config (.yml) file.")
flags.DEFINE_string("model", "{}", "Options: chatbot.{DynamicBot,Simplebot,ChatBot}.")
flags.DEFINE_string("model_params", "{}", "")
flags.DEFINE_string("dataset", "{}", "Options: data.{Cornell,Ubuntu,WMT}.")
flags.DEFINE_string("dataset_params", "{}", "")
FLAGS = flags.FLAGS


def start_training(dataset, bot):
    """Train bot. Will expand this function later to aid interactivity/updates."""
    print("Training bot. CTRL-C to stop training.")
    bot.train(dataset)


def start_chatting(bot):
    """Talk to bot. Will add teacher mode soon. Old implementation in _decode.py."""
    print("Initiating chat session.")
    print("Your bot has a temperature of %.2f." % bot.temperature, end=" ")
    if bot.temperature < 0.1:
        print("Not very adventurous, are we?")
    elif bot.temperature < 0.7:
        print("This should be interesting . . . ")
    else:
        print("Enjoy your gibberish!")
    bot.chat()


def main(argv):

    # Extract the merged configs/dictionaries.
    config = io_utils.parse_config(FLAGS)
    if config['model_params']['decode'] and config['model_params']['reset_model']:
        print("Setting reset to false for chat session . . . ")
        config['model_params']['reset_model'] = False
    # If loading from pretrained, double-check that certain values are correct.
    if FLAGS.pretrained_dir is not None:
        assert config['model_params']['decode'] \
               and not config['model_params']['reset_model']

    # Print out any non-default parameters given by user, so as to reassure
    # them that everything is set up properly.
    io_utils.print_non_defaults(config)

    print("Setting up %s dataset." % config['dataset'])
    dataset_class = locate(config['dataset']) or getattr(data, config['dataset'])
    dataset = dataset_class(config['dataset_params'])
    print("Creating", config['model'], ". . . ")
    bot_class = locate(config['model']) or getattr(chatbot, config['model'])
    bot = bot_class(dataset, config)

    if not config['model_params']['decode']:
        start_training(dataset, bot)
    else:
        start_chatting(bot)

if __name__ == "__main__":
    tf.logging.set_verbosity(tf.logging.WARN)
    tf.app.run()

