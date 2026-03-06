#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import smach
from subprocess import call, Popen

# ==========================================
# 1. State（状態）の定義
# ==========================================

class ListenState(smach.State):
    """音声を聞き取り、目的地をUserdataに書き込むステート"""
    def __init__(self):
        smach.State.__init__(self, 
                             outcomes=['success', 'failed'],
                             # このステートが「出力（書き込み）」するデータのキー名を宣言
                             output_keys=['target_location_out'])

    def execute(self, userdata):
        rospy.loginfo("ロボット: どこへ移動しますか？ (kitchen / living / entrance)")
        rospy.sleep(1.0)
        
        # 疑似的な音声認識結果
        recognized_word = "kitchen"
        rospy.loginfo(f"ロボット: '{recognized_word}' と聞こえました。")
        
        if recognized_word:
            # 宣言したキー名を使って、userdataにデータを格納する
            userdata.target_location_out = recognized_word
            return 'success'
        else:
            return 'failed'

class MoveToLocationState(smach.State):
    """Userdataから目的地を読み取り、移動するステート"""
    def __init__(self):
        smach.State.__init__(self, 
                             outcomes=['arrived'],
                             # このステートが「入力（読み取り）」するデータのキー名を宣言
                             input_keys=['destination_in'])

    def execute(self, userdata):
        # 宣言したキー名を使って、userdataからデータを取り出す
        target = userdata.destination_in
        rospy.loginfo(f"ロボット: {target} へ移動を開始します...")
        rospy.sleep(2.0)
        call("rostopic pub /turtle1/cmd_vel geometry_msgs/Twist '{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: -1.8}}'", shell=True)
        
        rospy.loginfo(f"ロボット: {target} に到着しました。")
        return 'arrived'

# ==========================================
# 2. StateMachineの構築とデータの紐付け（Remapping）
# ==========================================

def main():
    rospy.init_node('smach_userdata_tutorial')

    sm = smach.StateMachine(outcomes=['FINISHED', 'ERROR'])
    
    # StateMachine全体で使う共通のデータボックス（初期値）を定義しておくことも可能
    sm.userdata.shared_location = ""

    with sm:
        # ListenStateの追加
        # remapping: ステート内の変数名(target_location_out)を、全体共有の変数名(shared_location)に繋ぎ変える
        smach.StateMachine.add('LISTEN', ListenState(), 
                               transitions={'success': 'MOVE', 
                                            'failed': 'ERROR'},
                               remapping={'target_location_out': 'shared_location'})

        # MoveToLocationStateの追加
        # remapping: 全体共有の変数名(shared_location)を、ステート内の変数名(destination_in)に繋ぎ変える
        smach.StateMachine.add('MOVE', MoveToLocationState(), 
                               transitions={'arrived': 'FINISHED'},
                               remapping={'destination_in': 'shared_location'})

    rospy.loginfo("=== ステートマシン開始 ===")
    sm.execute()
    rospy.loginfo("=== ステートマシン終了 ===")

if __name__ == '__main__':
    main()