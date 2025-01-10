from .character_state import CharacterState
'''
{
        public const int LLM_MSG_WALK_TO_DO = 1001;
        public const int LLM_MSG_ACTION = 1002;
        public const int LLM_MSG_NFT = 1003;
        public const int LLM_USER_BUY_ARTWORK_RESULT = 1004;
        public const int LLM_USER_SELL_ARTWORK_RESULT = 1005;
        public const int LLM_AGENT_ARTWORK_TRADE = 1006;
        public const int LLM_MSG_WALK_TO = 1007;
        public const int LLM_MSG_SPEAK = 1008;
        public const int LLM_ARTWORK_RECYCLE_PRICE_DESC = 1010;
        public const int LLM_MSG_RECEIVE_SUBSISTENCE_ALLOWANCES = 1011;
        public const int LLM_MSG_BIRTH_REQUEST = 1012;

        public const int SERVER_MSG_INIT = 2000;
        public const int SERVER_MSG_WALK_STOPPED = 2001;
        public const int SERVER_MSG_ON_NEW_DAY = 2002;
        public const int SERVER_MSG_AGENT_ATTR_CHANGE = 2003;
        public const int SERVER_MSG_USER_BUY_ARTWORK = 2004;
        public const int SERVER_MSG_USER_SELL_ARTWORK = 2005;
        public const int SERVER_MSG_CMD = 2006;
        public const int SERVER_MSG_ACK = 2007;
        public const int SERVER_MSG_AGENT_BORN = 2008;
    }
'''

AllStateMsg = [2008] # handle once the message is recieved

State2RecieveMsgId = { CharacterState.MOVE: 2001,
                      CharacterState.USERTRADE: [2004, 2005],
        }

State2PushMsgId = { CharacterState.MOVE: 1007,
                   CharacterState.SUM: 1002,
                    CharacterState.ACT: 1007,
                    CharacterState.DRAW: 1003,
                   }
                     
                