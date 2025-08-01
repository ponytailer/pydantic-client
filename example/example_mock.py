"""
Example for using mock functionality in pydantic-client
"""
import logging
from typing import List, Optional
from pydantic import BaseModel

from pydantic_client.sync_client import RequestsWebClient
from pydantic_client.decorators import get, post, patch

# 设置日志格式和级别
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 定义API响应模型
class User(BaseModel):
    name: str
    age: int
    email: Optional[str] = None


class UserList(BaseModel):
    users: List[User]
    total: int


# 定义API客户端
class MockableApiClient(RequestsWebClient):
    @get("/users")
    def get_users(self) -> UserList:
        """获取用户列表"""
        pass
    
    @get("/users/{user_id}")
    def get_user(self, user_id: int) -> User:
        """获取单个用户"""
        pass
    
    @post("/users")
    def create_user(self, user: User) -> User:
        """创建用户"""
        pass
    
    @patch("/users/{user_id}")
    def update_user(self, user_id: int, user: User) -> User:
        """更新用户"""
        pass


def main():
    # 创建客户端
    client = MockableApiClient(base_url="https://api.example.com")
    
    # 设置mock数据
    client.set_mock_config(mock_config=[
        {
            "name": "get_users",
            "output": {
                "users": [
                    {"name": "张三", "age": 30, "email": "zhangsan@example.com"},
                    {"name": "李四", "age": 25, "email": "lisi@example.com"}
                ],
                "total": 2
            }
        },
        {
            "name": "get_user",
            "output": {
                "name": "张三",
                "age": 30,
                "email": "zhangsan@example.com"
            }
        },
        {
            "name": "create_user",
            "output": {
                "name": "王五",
                "age": 35,
                "email": "wangwu@example.com"
            }
        }
    ])
    
    # 使用API方法 - 将返回mock数据而不是实际发送请求
    users = client.get_users()
    print(f"用户列表: {users.users}")
    print(f"总用户数: {users.total}")
    
    user = client.get_user(1)
    print(f"单个用户: {user.name}, {user.age} 岁")
    
    new_user = User(name="王五", age=35, email="wangwu@example.com")
    created_user = client.create_user(new_user)
    print(f"创建的用户: {created_user.name}, {created_user.email}")
    
    # 没有mock配置的方法会尝试实际API调用
    # 注意: 下面这行代码会尝试实际发送请求,因为我们没有为update_user设置mock
    # 在这个示例中会失败,因为我们的API地址不存在
    # try:
    #     updated_user = client.update_user(1, new_user)
    #     print(f"更新的用户: {updated_user.name}")
    # except Exception as e:
    #     print(f"API调用失败(预期的行为): {e}")


def from_config_example():
    """演示使用from_config创建带mock配置的客户端"""
    config = {
        "base_url": "https://api.example.com",
        "timeout": 10,
        "mock_config": [
            {
                "name": "get_users",
                "output": {
                    "users": [
                        {"name": "配置张三", "age": 30, "email": "config_zhangsan@example.com"},
                        {"name": "配置李四", "age": 25, "email": "config_lisi@example.com"}
                    ],
                    "total": 2
                }
            }
        ]
    }
    
    client = MockableApiClient.from_config(config)
    users = client.get_users()
    print("\n从配置创建的客户端:")
    print(f"用户列表: {users.users}")


if __name__ == "__main__":
    main()
    from_config_example()
