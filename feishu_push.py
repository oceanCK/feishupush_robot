'''
飞书机器人webhook信息推送脚本
'''
import requests
import argparse

# 设置参数化信息推送，包含平台，版本，名称，构建时间等，推送到飞书机器人
def push_msg(push_args=None):

    headers = {
        "Content-Type": "application/json"
    }
    # 机器人的webhook地址
    Robot_hook = "https://www.feishu.cn/flow/api/trigger-webhook/6913c2007086d1c6107a6fb665f7aba7"

    # webhook推送的数据，可增删改参数
    data = {
       "msg_type": "text",
       "content": {
            "name": f"{push_args.name}",
            "task": f"{push_args.task}",
            "priority": f"{push_args.priority}",
            "status": f"{push_args.status}"
       }
    }
    
    try:       
        response = requests.post(Robot_hook, json=data, headers=headers)
        response.raise_for_status()
        print("Message pushed successfully.")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error pushing message: {e}")
        return
    
def argument_parser():
    parser = argparse.ArgumentParser(description='推送任务类型')
    parser.add_argument('--name', type=str, action='store', default="None", help='推送人指定')
    parser.add_argument('--task', type=str, action='store', default="None", help='任务名')
    parser.add_argument('--priority', type=str, required=True, action='store', help='优先级')
    parser.add_argument('--status', type=str, required=True, action='store', default="None", help='目前情况')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = argument_parser()
    push_msg(args)