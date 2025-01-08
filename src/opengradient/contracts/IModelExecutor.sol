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
     * This function will be called by the OG-Model-Executor module.
     */
    function run() external;

    /**
     * @dev Retrieves the result of the last executed model task.
     * @return A `ModelOutput` struct representing the result of the model task.
     */
    function getInferenceResult() external view returns (ModelOutput memory);
}