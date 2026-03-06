#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import smach
from std_msgs.msg import String
from subprocess import call, Popen


# 疑似的なステート定義（中身は省略）
class MoveState(smach.State):
    def __init__(self, pub):
        smach.State.__init__(self, outcomes=['done'])
        self.pub = pub

    def execute(self, userdata): 
        rospy.sleep(1)
        
        hello_str = String(data="move done")
        self.pub.publish(hello_str)

        # 修正: subprocess.callを使用し、rostopic pubには「-1 (1回送信して終了)」オプションを付与
        cmd = "rostopic pub -1 /turtle1/cmd_vel geometry_msgs/Twist '{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: -1.8}}'"
        call(cmd, shell=True)

        return 'done'

class SearchState(smach.State):
    def __init__(self, pub):
        smach.State.__init__(self, outcomes=['found', 'not_found'])
        self.pub = pub

    def execute(self, userdata): 
        rospy.sleep(1)

        hello_str = String(data="search done")
        self.pub.publish(hello_str)

        return 'found'

class ReportState(smach.State):
    def __init__(self, pub):
        smach.State.__init__(self, outcomes=['done'])
        self.pub = pub

    def execute(self, userdata): 
        rospy.sleep(1)

        hello_str = String(data="report done")
        self.pub.publish(hello_str)

        return 'done'

def main():
    # 1. ノードの初期化（プロセス内で1回のみ実行）
    rospy.init_node('smach_nesting_tutorial')

    # 2. ROS通信リソースの作成（グローバルではなくmain関数内で管理）
    pub = rospy.Publisher('chatter', String, queue_size=10)

    # ==========================================
    # 1. サブのステートマシン（巡回タスク）を作成
    # ==========================================
    # このサブマシン自体が、外部に対して 'sub_success' か 'sub_fail' を返す
    sm_patrol = smach.StateMachine(outcomes=['sub_success', 'sub_fail'])
    with sm_patrol:
        smach.StateMachine.add('MOVE_TO_ROOM', MoveState(pub),
                               transitions={'done': 'SEARCH_ITEM'})
        smach.StateMachine.add('SEARCH_ITEM', SearchState(pub),
                               transitions={'found': 'sub_success',
                                            'not_found': 'sub_fail'})

    # ==========================================
    # 2. メインのステートマシンを作成し、サブをネストする
    # ==========================================
    sm_top = smach.StateMachine(outcomes=['ALL_FINISHED', 'ERROR'])
    with sm_top:
        # サブステートマシン(sm_patrol)を、1つのステートとして追加
        smach.StateMachine.add('PATROL_TASK', sm_patrol,
                               transitions={'sub_success': 'REPORT',
                                            'sub_fail': 'ERROR'})

        smach.StateMachine.add('REPORT', ReportState(pub),
                               transitions={'done': 'ALL_FINISHED'})

    sm_top.execute()

if __name__ == '__main__':
    main()