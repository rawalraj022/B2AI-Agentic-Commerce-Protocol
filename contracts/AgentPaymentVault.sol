// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./interfaces/IERC20.sol";

/// @title AgentPaymentVault
/// @notice Policy-controlled settlement vault for AI agents.
/// Enforces: no double-spend, no over-amount, no expiry, no wrong merchant,
/// no reused credential. The vault holds XSGD and settles authorized payments.
contract AgentPaymentVault {
    IERC20 public immutable xsgd;

    struct Authorization {
        address wallet;      // self-custodied wallet that funded the auth
        address merchant;    // merchant address
        uint256 amount;      // authorized amount (in XSGD base units)
        uint256 expiry;      // unix timestamp
        bytes32 commitment;  // H(wallet, merchant, sku, amount, nonce, expiry)
        bool executed;
    }

    mapping(bytes32 => Authorization) public authorizations;
    mapping(bytes32 => bool) public usedCredentials;

    event Authorized(bytes32 indexed commitment, address wallet, address merchant, uint256 amount);
    event Settled(bytes32 indexed commitment, address merchant, uint256 amount);
    event Cancelled(bytes32 indexed commitment);

    constructor(address _xsgd) {
        xsgd = IERC20(_xsgd);
    }

    /// @notice Register an authorization on-chain.
    function authorizePayment(
        address wallet,
        address merchant,
        uint256 amount,
        uint256 expiry,
        bytes32 commitment
    ) external {
        require(block.timestamp < expiry, "Authorization already expired");
        require(authorizations[commitment].amount == 0, "Authorization already exists");
        authorizations[commitment] = Authorization({
            wallet: wallet,
            merchant: merchant,
            amount: amount,
            expiry: expiry,
            commitment: commitment,
            executed: false
        });
        emit Authorized(commitment, wallet, merchant, amount);
    }

    /// @notice Settle an authorized payment by transferring XSGD to the merchant.
    /// The vault must hold sufficient XSGD (funded by the wallet).
    function settlePayment(
        bytes32 commitment,
        address merchant,
        uint256 amount,
        bytes32 credentialHash
    ) external {
        Authorization storage auth = authorizations[commitment];
        require(auth.amount != 0, "Authorization not found");
        require(!auth.executed, "Already settled (double spend)");
        require(block.timestamp < auth.expiry, "Authorization expired");
        require(merchant == auth.merchant, "Wrong merchant");
        require(amount <= auth.amount, "Amount exceeds authorization");
        require(!usedCredentials[credentialHash], "Credential already used");

        auth.executed = true;
        usedCredentials[credentialHash] = true;

        require(xsgd.transfer(merchant, amount), "XSGD transfer failed");
        emit Settled(commitment, merchant, amount);
    }

    /// @notice Cancel an authorization before it is executed.
    function cancelAuthorization(bytes32 commitment) external {
        Authorization storage auth = authorizations[commitment];
        require(auth.amount != 0, "Authorization not found");
        require(!auth.executed, "Already settled");
        auth.executed = true; // mark as consumed so it cannot be settled
        emit Cancelled(commitment);
    }
}