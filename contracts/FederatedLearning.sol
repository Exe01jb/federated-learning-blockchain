pragma solidity ^0.8.19;

contract FederatedLearning {
    address public owner;
    uint256 public currentRound;
    uint256 public minParticipants;
    uint256 public rewardPerRound;

    struct Participant {
        bool registered;
        uint256 reputation;
        uint256 totalRewards;
    }

    struct ModelUpdate {
        address participant;
        bytes32 modelHash;
        string modelCID;
        uint256 dataSize;
        uint256 timestamp;
    }

    struct RoundInfo {
        bytes32 globalModelHash;
        string globalModelCID;
        uint256 numUpdates;
        bool finalized;
    }

    mapping(address => Participant) public participants;
    mapping(uint256 => ModelUpdate[]) private roundUpdates;
    mapping(uint256 => RoundInfo) public rounds;
    address[] public participantList;

    event ParticipantRegistered(address indexed participant);
    event ModelUpdateSubmitted(address indexed participant, uint256 indexed round, bytes32 modelHash);
    event RoundFinalized(uint256 indexed round, bytes32 globalModelHash, uint256 numUpdates);
    event RewardDistributed(address indexed participant, uint256 indexed round, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner, "FL: caller is not the owner");
        _;
    }

    modifier onlyRegistered() {
        require(participants[msg.sender].registered, "FL: participant not registered");
        _;
    }

    constructor(uint256 _minParticipants, uint256 _rewardPerRound) {
        require(_minParticipants > 0, "FL: minParticipants must be > 0");
        owner = msg.sender;
        minParticipants = _minParticipants;
        rewardPerRound = _rewardPerRound;
        currentRound = 0;
    }

    function registerParticipant() external {
        require(!participants[msg.sender].registered, "FL: already registered");
        participants[msg.sender] = Participant({registered: true, reputation: 0, totalRewards: 0});
        participantList.push(msg.sender);
        emit ParticipantRegistered(msg.sender);
    }


    function submitModelUpdate(bytes32 _modelHash, string calldata _modelCID, uint256 _dataSize) external onlyRegistered {
        require(_dataSize > 0, "FL: dataSize must be > 0");
        require(!rounds[currentRound].finalized, "FL: round already finalized");

        roundUpdates[currentRound].push(
            ModelUpdate({
                participant: msg.sender,
                modelHash: _modelHash,
                modelCID: _modelCID,
                dataSize: _dataSize,
                timestamp: block.timestamp
            })
        );

        emit ModelUpdateSubmitted(msg.sender, currentRound, _modelHash);
    }


    function finalizeRound(bytes32 _globalModelHash, string calldata _globalModelCID) external onlyOwner {
        uint256 count = roundUpdates[currentRound].length;
        require(count >= minParticipants, "FL: not enough updates yet");

        rounds[currentRound] = RoundInfo({
            globalModelHash: _globalModelHash,
            globalModelCID: _globalModelCID,
            numUpdates: count,
            finalized: true
        });

        _distributeRewards(currentRound);

        emit RoundFinalized(currentRound, _globalModelHash, count);
        currentRound += 1;
    }

    function _distributeRewards(uint256 _round) internal {
        ModelUpdate[] storage updates = roundUpdates[_round];
        uint256 share = rewardPerRound / updates.length;

        for (uint256 i = 0; i < updates.length; i++) {
            address p = updates[i].participant;
            participants[p].totalRewards += share;
            participants[p].reputation += 1;
            emit RewardDistributed(p, _round, share);
        }
    }

    function getRoundUpdates(uint256 _round) external view returns (ModelUpdate[] memory) {
        return roundUpdates[_round];
    }

    function getParticipantCount() external view returns (uint256) {
        return participantList.length;
    }
}
