#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from control_msgs.action import FollowJointTrajectory, GripperCommand
from rclpy.action import ActionServer, GoalResponse, CancelResponse
import math
import traceback
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig


class SOARM101Controller(Node):
    def __init__(self):
        super().__init__('soarm101_controller')

        # Robot setup
        cfg = SO101FollowerConfig(port="/dev/ttyACM0", id="Follower")
        self.robot = SO101Follower(cfg)
        self.robot.connect()
        self.robot.calibrate()

        # Arm action server (FollowJointTrajectory)
        self.arm_as = ActionServer(
            self,
            FollowJointTrajectory,
            'soarm101_controller/follow_joint_trajectory',
            execute_callback=self.execute_arm_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )

        # Gripper action server (GripperCommand)
        self.gripper_as = ActionServer(
            self,
            GripperCommand,
            'soarm101_controller/gripper_cmd',
            execute_callback=self.execute_gripper_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )

        self.get_logger().info("SOARM101 Controller is up!")

    def goal_callback(self, goal_request):
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        return CancelResponse.ACCEPT


    async def execute_arm_callback(self, goal_handle):
        self.get_logger().info("Executing arm trajectory")
        traj = goal_handle.request.trajectory

        for pt in traj.points:
            positions_rad = list(pt.positions)
            self.get_logger().info(f"Received (rad): {positions_rad}")

            positions_deg = [p * 180.0 / 3.14159 for p in positions_rad]

            # Map to motor names with `.pos`
            goal_pos = {
                "shoulder_pan.pos": positions_deg[0],
                "shoulder_lift.pos": positions_deg[1],
                "elbow_flex.pos": positions_deg[2],
                "wrist_flex.pos": positions_deg[3],
                "wrist_roll.pos": positions_deg[4],
                "gripper.pos": positions_deg[5],  # 0–100 range for gripper
            }

            self.get_logger().info(f"Converted positions: {goal_pos}")

            try:
                self.robot.send_action(goal_pos)
            except Exception as e:
                self.get_logger().error(f"Error sending action: {e}")

        goal_handle.succeed()
        return FollowJointTrajectory.Result()


    async def execute_gripper_callback(self, goal_handle):
        self.get_logger().info("Executing gripper command")
        cmd = goal_handle.request.command

        self.robot.send_action({"gripper.pos": cmd.position})

        goal_handle.succeed()
        result = GripperCommand.Result()
        result.position = cmd.position
        result.effort = cmd.max_effort
        result.stalled = False
        result.reached_goal = True
        return result


def main(args=None):
    rclpy.init(args=args)
    node = SOARM101Controller()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.robot.disconnect()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
