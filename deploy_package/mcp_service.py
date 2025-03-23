#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import paramiko
import argparse
from pathlib import Path


class MCPService:
    """MCP服务类，提供连接Linux服务器、执行命令和上传文件的功能"""
    
    def __init__(self, host, port, username, password=None, key_file=None):
        """
        初始化MCP服务
        
        参数:
            host: 服务器主机名或IP
            port: SSH端口
            username: 用户名
            password: 密码（与key_file二选一）
            key_file: 私钥文件路径（与password二选一）
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_file = key_file
        self.client = None
        self.sftp = None
    
    def connect(self):
        """连接到Linux服务器"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 使用密钥或密码登录
            if self.key_file:
                key = paramiko.RSAKey.from_private_key_file(self.key_file)
                self.client.connect(self.host, self.port, self.username, pkey=key)
            else:
                self.client.connect(self.host, self.port, self.username, self.password)
            
            # 创建SFTP客户端
            self.sftp = self.client.open_sftp()
            print(f"成功连接到服务器 {self.host}")
            return True
        except Exception as e:
            print(f"连接服务器失败: {str(e)}")
            return False
    
    def execute_command(self, command):
        """
        在Linux服务器上执行命令
        
        参数:
            command: 要执行的命令
            
        返回:
            stdout: 标准输出
            stderr: 标准错误
        """
        if not self.client:
            print("未连接到服务器，请先调用connect()方法")
            return None, None
        
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            stdout_str = stdout.read().decode('utf-8')
            stderr_str = stderr.read().decode('utf-8')
            
            print(f"命令执行完成: {command}")
            if stdout_str:
                print("标准输出:")
                print(stdout_str)
            if stderr_str:
                print("标准错误:")
                print(stderr_str)
                
            return stdout_str, stderr_str
        except Exception as e:
            print(f"执行命令失败: {str(e)}")
            return None, None
    
    def upload_file(self, local_path, remote_path):
        """
        上传文件到Linux服务器
        
        参数:
            local_path: 本地文件路径
            remote_path: 远程文件路径
            
        返回:
            bool: 是否上传成功
        """
        if not self.sftp:
            print("未连接到服务器，请先调用connect()方法")
            return False
        
        try:
            self.sftp.put(local_path, remote_path)
            print(f"文件上传成功: {local_path} -> {remote_path}")
            return True
        except Exception as e:
            print(f"文件上传失败: {str(e)}")
            return False
    
    def download_file(self, remote_path, local_path):
        """
        从Linux服务器下载文件
        
        参数:
            remote_path: 远程文件路径
            local_path: 本地文件路径
            
        返回:
            bool: 是否下载成功
        """
        if not self.sftp:
            print("未连接到服务器，请先调用connect()方法")
            return False
        
        try:
            self.sftp.get(remote_path, local_path)
            print(f"文件下载成功: {remote_path} -> {local_path}")
            return True
        except Exception as e:
            print(f"文件下载失败: {str(e)}")
            return False
    
    def disconnect(self):
        """断开与Linux服务器的连接"""
        if self.sftp:
            self.sftp.close()
        if self.client:
            self.client.close()
        print("已断开与服务器的连接")


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='MCP服务 - 连接Linux服务器、执行命令和上传文件')
    parser.add_argument('--host', required=True, help='服务器主机名或IP')
    parser.add_argument('--port', type=int, default=22, help='SSH端口')
    parser.add_argument('--username', required=True, help='用户名')
    parser.add_argument('--password', help='密码（与key_file二选一）')
    parser.add_argument('--key-file', help='私钥文件路径（与password二选一）')
    
    subparsers = parser.add_subparsers(dest='command', help='要执行的操作')
    
    # 执行命令子命令
    cmd_parser = subparsers.add_parser('cmd', help='执行命令')
    cmd_parser.add_argument('cmd_str', help='要执行的命令')
    
    # 上传文件子命令
    upload_parser = subparsers.add_parser('upload', help='上传文件')
    upload_parser.add_argument('local_path', help='本地文件路径')
    upload_parser.add_argument('remote_path', help='远程文件路径')
    
    # 下载文件子命令
    download_parser = subparsers.add_parser('download', help='下载文件')
    download_parser.add_argument('remote_path', help='远程文件路径')
    download_parser.add_argument('local_path', help='本地文件路径')
    
    args = parser.parse_args()
    
    # 创建并连接服务
    service = MCPService(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        key_file=args.key_file
    )
    
    if not service.connect():
        return
    
    try:
        # 执行对应的操作
        if args.command == 'cmd':
            service.execute_command(args.cmd_str)
        elif args.command == 'upload':
            service.upload_file(args.local_path, args.remote_path)
        elif args.command == 'download':
            service.download_file(args.remote_path, args.local_path)
        else:
            print("连接成功！使用 --help 查看可用的命令")
    finally:
        service.disconnect()


if __name__ == "__main__":
    main() 