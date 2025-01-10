import redis
import datetime
import json

def insert_to_redis(handle, key, value):
    while True:
        handle.set(key, value)
        try:
            handle.set(key, value)
            print("insert success")
            break
        except:
            print("insert error")

def read_from_redis(handle, keys):
    if isinstance(keys, list):
        while True:
            try:
                result = handle.mget(keys)
                print("read success")
                break
            except:
                print("read error")
                
    elif isinstance(keys, str):
        while True:
            try:
                result = handle.get(keys)
                print("read success")
                break
            except:
                print("read error")
    return result

def redis_test():
    r = redis.Redis(host='13.55.217.68', 
                    port=6379, 
                    password='Pandai_123',
                    db=0)


    while True:
        try:
            r.set('agent/000/txt/mood', 'fear:6')
            print('success')
            break
        except:
            print('error')
    while True:
        try:
            r.set('agent/000/txt/log', 'test from joe: trade with no.2')
            print('success')
            break
        except:
            print('error')
    while True:
        try:        
            r.set('agent/000/txt/economy', 'income 2$') 
            print('success')
            break
        except:
            print('error')
    while True:
        try:
            print(r.mget(['agent/000/txt/mood', 'agent/000/txt/log', 'agent/000/txt/economy']))  # 应该显示 b'value
            break
        except:
            print("error and wait")
            
def mysql_test():
    import mysql.connector
    config = {
        'host': '13.55.217.68', 
        'user': 'dev',  
        'password': 'Pandai_dev_123',  
        'port': 3306,
        'database': 'game'
    }
    try:
        # 建立连接
        connection = mysql.connector.connect(**config)
        print("数据库连接成功")

        # 创建一个cursor对象，用于执行SQL语句
        # insert_sql = "INSERT INTO agent (agent_id, primitive, creativity, charm, art_style, character, rebeliousness, energy, gold, health, is_unpack, is_enter_city, user_id, create_time, unpack_time, modify_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        insert_sql = "INSERT INTO artwork (artwrok_id, create_time, agent_id) VALUES (%s, %s, %s)"
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # values = ('000', 0, 0, 0, 'fake', 'intj', '0', 9, 1000, 6, 0, 0, 'joe', now, now, now)
        values = ('109', now, 1)
        cursor = connection.cursor()
        cursor.execute(insert_sql, values)
                
        # 执行SQL查询（例如：选择所有数据）
        cursor.execute("SELECT * FROM artwork")
        result = cursor.fetchall()
        
    
        # 打印查询结果
        for row in result:
            print(row)
        
        
    except mysql.connector.Error as error:
        print(f"数据库连接失败: {error}")

    finally:
        # 关闭数据库连接
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL连接已关闭")

if __name__ == "__main__":
    # redis_test()
    # mysql_test()
    emo_1 = "The agent's is somewhat in fear"
    # percept_1 = {'AnalyseExternalObservations': [{'perception': {'category': 'people', 'object': 'Jack Brown', 'description': 'Jack Brown is None with no one'}, 'word_understanding': "1) Typically, people interact with others in public spaces. 2) 'None with no one' suggests lack of interaction or activity, which is unusual in a social setting.", 'difference_level': 5}, {'perception': {'category': 'people', 'object': 'Lily Johnson', 'description': 'Lily Johnson is None with no one'}, 'word_understanding': "1) Social interaction is common in public areas. 2) 'None with no one' indicates absence of social or physical activity, which is not typical.", 'difference_level': 5}, {'perception': {'category': 'people', 'object': 'Noah Davis', 'description': 'Noah Davis is None with no one'}, 'word_understanding': '1) People usually engage with their surroundings or others when outside. 2) The description suggests an unusual state of isolation or inactivity.', 'difference_level': 5}, {'perception': {'category': 'people', 'object': 'Olivia Miller', 'description': 'Olivia Miller is None with no one'}, 'word_understanding': "1) Outdoor areas are typically places of activity and interaction. 2) 'None with no one' implies an unexpected level of inactivity or isolation.", 'difference_level': 5}], 'AnalyseInternalPerceptions': [{'perception': {'attribute': 'money', 'value': '1000'}, 'word_understanding': 'Sufficient funds for gambling activities or investments, aligns with professional gambler status.', 'difference_level': 0}, {'perception': {'attribute': 'health', 'value': '10/10'}, 'word_understanding': 'Optimal health condition, ideal for undertaking any planned activities.', 'difference_level': 0}, {'perception': {'attribute': 'satiety', 'value': '10/10'}, 'word_understanding': 'Fully satiated, no immediate need for food, which is ideal for focusing on tasks at hand.', 'difference_level': 0}, {'perception': {'attribute': 'vigor', 'value': '100/100'}, 'word_understanding': 'Full of energy, perfectly suited for engaging in any demanding activities or plans.', 'difference_level': 0}, {'perception': {'attribute': 'trust', 'value': '5/10'}, 'word_understanding': 'Moderate level of trust, suggests uncertainty in social interactions or relationships, which could be improved.', 'difference_level': 5}], 'AnalysePlanAction': []}
    goal_1 = 'I should mitigate the discrepancy between the current situation of Jack Brown being alone and the ideal stable status of social interaction.'
    act_1 = "The agent MOVE to Disco. It's purpose: organize and participate in the monthly dance nights to encourage socializing and fun"
    test_data_1 = {
        "agent/1/txt/mood":emo_1,
        "agent/1/txt/log":act_1,
        "agent/1/txt/economy":'sell the artwork 00001 to agent2 by 100$',
        "agent/1/txt/thinking": goal_1,
        "agent/1/txt/money":"1000",
        "agent/1/txt/artwork_num":1,
        "agent/1/txt/children_num":0,
        "agent/1/txt/conversation": "Jack brown talked to Lily Doe in 2024-04-02 15:21:30"
        
    }
    handle = redis.Redis(host='13.55.217.68', 
                        port=6379, 
                        password='Pandai_123',
                        db=0)
    for key, value in test_data_1.items():
        insert_to_redis(handle, key, value)