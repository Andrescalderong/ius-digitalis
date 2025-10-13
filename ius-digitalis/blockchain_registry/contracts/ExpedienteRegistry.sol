// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ExpedienteRegistry {
    event ExpedienteRegistrado(string expedienteId, bytes32 documentoHash, uint256 timestamp);
    mapping(string => bytes32) private hashes;

    function registrar(string calldata expedienteId, bytes32 documentoHash) external {
        require(hashes[expedienteId] == bytes32(0), "Ya existe");
        hashes[expedienteId] = documentoHash;
        emit ExpedienteRegistrado(expedienteId, documentoHash, block.timestamp);
    }

    function verificar(string calldata expedienteId, bytes32 documentoHash) external view returns (bool) {
        return hashes[expedienteId] == documentoHash;
    }
}
