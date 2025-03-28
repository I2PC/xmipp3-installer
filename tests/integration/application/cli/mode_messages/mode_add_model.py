from .. import terminal_sizes
from . import NOTE_MESSAGE

HELP_MESSAGE = {
  terminal_sizes.LARGE_TERMINAL_WIDTH: f"""Takes a DeepLearning model from the modelPath, makes a tgz of it and uploads the .tgz according to the <login>.
This mode is used to upload a model folder to the Scipion/Xmipp server.
Usually the model folder contains big files used to feed deep learning procedures with pretrained data. All the models stored in the server will be downloaded using the 'get_models' mode, during the compilation/installation time, or with scipion3 installb deepLearningToolkit.
Param <modelsPath> must be an absolute path.

Usage: -> ./xmipp addModel <usr@server> <modelsPath> [--update]
Steps:  0. modelName = basename(modelsPath) <- Please, check the folders name!
        1. Packing in 'xmipp_model_modelName.tgz'
        2. Check if that model already exists (use --update to override an existing model)
        3. Upload the model to the server.
        4. Update the MANIFEST file.

The model name will be the folder name in <modelsPath>
Must have write permissions to such machine.

{NOTE_MESSAGE}Usage: xmipp addModel [options]
    ---------------------------------------------
    # Options #

    login                                          Login (usr@server) for remote host to upload the model with. Must have write permissions to such machine.
    modelPath                                      Path to the model to upload to remote host.
    --update                                       Flag to update an existing model

Example: ./xmipp addModel myuser@127.0.0.1 /home/myuser/mymodel
""",
  terminal_sizes.SHORT_TERMINAL_WIDTH: f"""Takes a DeepLearning model from the modelPath, makes a tgz of it and uploads the .tgz according to the <login>.
This mode is used to upload a model folder to the Scipion/Xmipp server.
Usually the model folder contains big files used to feed deep learning procedures with pretrained data. All the models stored in the server will be downloaded using the 'get_models' mode, during the compilation/installation time, or with scipion3 installb deepLearningToolkit.
Param <modelsPath> must be an absolute path.

Usage: -> ./xmipp addModel <usr@server> <modelsPath> [--update]
Steps:  0. modelName = basename(modelsPath) <- Please, check the folders name!
        1. Packing in 'xmipp_model_modelName.tgz'
        2. Check if that model already exists (use --update to override an existing model)
        3. Upload the model to the server.
        4. Update the MANIFEST file.

The model name will be the folder name in <modelsPath>
Must have write permissions to such machine.

{NOTE_MESSAGE}Usage: xmipp addModel [options]
    ---------------------------------------------
    # Options #

    login                                          Login (usr@server) for
                                                   remote host to upload the
                                                   model with. Must have
                                                   write permissions to such
                                                   machine.
    modelPath                                      Path to the model to
                                                   upload to remote host.
    --update                                       Flag to update an
                                                   existing model

Example: ./xmipp addModel myuser@127.0.0.1 /home/myuser/mymodel
"""
}
