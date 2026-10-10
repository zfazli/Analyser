### Code Structure

This codebase consists of three main parts. The first part focuses on analyzing the training data and is located in the `data_process` directory.

The code for running Flash, Velox, and Orthrus is based on the implementation shared in the [PIDSMaker repository](https://github.com/ubc-provenance/PIDSMaker/). However, modifications were made to the original code to account for the removal of certain portions of the training data in our experiments. These modifications are documented in the `changes` directory.

Finally, the results of the analyses performed on the models and datasets are available in the `final_results` directory.