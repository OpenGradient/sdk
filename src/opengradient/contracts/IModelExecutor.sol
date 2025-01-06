// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "./og_inference/OGInference.sol"; // Import for shared types like ModelOutput, ModelInferenceRequest, etc.

/**
 * @title IModelExecutor
 * @dev Interface for contracts integrated with the OG-Model-Executor service.
 * Contracts implementing this interface must:
 * 1. Execute a model task via the `run` function.
 * 2. Provide access to the result of the model task using `getInferenceResult`.
 */
interface IModelExecutor {
    /**
     * @dev Executes the model task.
     * @param modelCID The CID of the model to run
     * @param inferenceMode The mode of inference (0=VANILLA, 1=ZK, 2=TEE)
     * @param input The model input data
     */
    function run(
        string memory modelCID,
        uint8 inferenceMode,
        ModelInput memory input
    ) external;

    /**
     * @dev Retrieves the result of the last executed model task.
     * @return A `ModelOutput` struct representing the result of the model task.
     */
    function getInferenceResult() external view returns (ModelOutput memory);
}