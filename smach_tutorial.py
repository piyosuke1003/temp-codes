#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import smach

# ==========================================
# 1. State（状態）の定義
# 各状態は独立したクラスとして定義します。
# 別のモジュールに切り出してimportすることも容易な設計です。
# ==========================================

class GreetingState(smach.State):
    """挨拶を行うステート"""
    def __init__(self):
        # このステートが出力しうるOutcome（結果）をリストで定義します
        smach.State.__init__(self, outcomes=['done'])

    def execute(self, userdata):
        # ここに具体的な処理を書きます
        rospy.loginfo("ロボット: こんにちは！タスクを開始します。")
        rospy.sleep(1.0)
        
        # 処理が終わったらOutcomeを返します
        return 'done'

class MovingState(smach.State):
    """移動を行うステート"""
    def __init__(self):
        # 成功と失敗、2つのOutcomeを定義します
        smach.State.__init__(self, outcomes=['success', 'failed'])

    def execute(self, userdata):
        rospy.loginfo("ロボット: 目的地へ移動中です...")
        rospy.sleep(2.0)
        
        # 疑似的な条件分岐（今回は必ず成功するとします）
        move_successful = True
        
        if move_successful:
            rospy.loginfo("ロボット: 到着しました。")
            return 'success'
        else:
            rospy.logwarn("ロボット: 障害物があり移動できませんでした。")
            return 'failed'

# ==========================================
# 2. StateMachine（状態遷移機械）の構築と実行
# どこからどこへ遷移するか（フロー制御）はここで一元管理します。
# ==========================================

def main():
    rospy.init_node('smach_tutorial_node')

    # 全体のステートマシンを作成します。
    # 最終的な終了状態（マシンの出口）となるOutcomeを定義します。
    sm = smach.StateMachine(outcomes=['TASK_COMPLETED', 'TASK_FAILED'])

    # コンテナを開いてステートと遷移ルールを追加していきます
    with sm:
        # 第一引数: ステートの名前
        # 第二引数: 実行するステートのインスタンス
        # 第三引数: 遷移ルール（Outcomeが〇〇のとき、△△のステートへ行く）
        
        smach.StateMachine.add('GREETING', GreetingState(), 
                               transitions={'done': 'MOVING'})

        # MOVINGステートの遷移先として、ステートマシン自体の出口（TASK_COMPLETED等）も指定できます
        smach.StateMachine.add('MOVING', MovingState(), 
                               transitions={'success': 'TASK_COMPLETED',
                                            'failed': 'TASK_FAILED'})

    # ステートマシンの実行を開始
    rospy.loginfo("=== ステートマシン開始 ===")
    outcome = sm.execute()
    rospy.loginfo(f"=== ステートマシン終了: 最終結果は {outcome} ===")

if __name__ == '__main__':
    main()