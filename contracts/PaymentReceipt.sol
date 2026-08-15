// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title PaymentReceipt
/// @notice On-chain proof-of-payment registry. Stores a verifiable link between
/// a card authorization (commitment) and the on-chain settlement that funded it.
contract PaymentReceipt {
    struct Receipt {
        bytes32 commitment;
        address wallet;
        address merchant;
        string sku;
        uint256 amount;
        uint256 timestamp;
        bytes32 transactionHash;
    }

    mapping(bytes32 => Receipt) public receipts;
    bytes32[] public receiptKeys;

    event ReceiptRecorded(bytes32 indexed commitment, address merchant, uint256 amount);

    /// @notice Record a receipt after settlement.
    function recordReceipt(
        bytes32 commitment,
        address wallet,
        address merchant,
        string calldata sku,
        uint256 amount,
        bytes32 transactionHash
    ) external {
        require(receipts[commitment].timestamp == 0, "Receipt already exists");
        receipts[commitment] = Receipt({
            commitment: commitment,
            wallet: wallet,
            merchant: merchant,
            sku: sku,
            amount: amount,
            timestamp: block.timestamp,
            transactionHash: transactionHash
        });
        receiptKeys.push(commitment);
        emit ReceiptRecorded(commitment, merchant, amount);
    }

    /// @notice Verify a receipt exists for a given commitment.
    function verifyReceipt(bytes32 commitment) external view returns (bool) {
        return receipts[commitment].timestamp != 0;
    }

    function getReceipt(bytes32 commitment) external view returns (Receipt memory) {
        return receipts[commitment];
    }

    function receiptCount() external view returns (uint256) {
        return receiptKeys.length;
    }
}