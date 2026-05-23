import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.actions import TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    rm_nav_bringup_dir = get_package_share_directory('rm_nav_bringup')
    overtake_dir = get_package_share_directory('venom_overtake_manager')
    venom_bringup_dir = get_package_share_directory('venom_bringup')

    use_sim_time = LaunchConfiguration('use_sim_time')
    world = LaunchConfiguration('world')
    dynamic_obstacles = LaunchConfiguration('dynamic_obstacles')
    lio = LaunchConfiguration('lio')
    localization = LaunchConfiguration('localization')
    nav_rviz = LaunchConfiguration('nav_rviz')
    lio_rviz = LaunchConfiguration('lio_rviz')
    overtake_params_file = LaunchConfiguration('overtake_params_file')
    road_network_file = LaunchConfiguration('road_network_file')
    route_name = LaunchConfiguration('route_name')
    mission_start_delay_sec = LaunchConfiguration('mission_start_delay_sec')

    sim_nav_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(rm_nav_bringup_dir, 'launch', 'bringup_sim.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'world': world,
            'dynamic_obstacles': dynamic_obstacles,
            'mode': 'nav',
            'localization': localization,
            'lio': lio,
            'nav_rviz': nav_rviz,
            'lio_rviz': lio_rviz,
        }.items(),
    )

    tracker_node = Node(
        package='venom_overtake_manager',
        executable='tracker_node',
        name='tracker_node',
        output='screen',
        parameters=[overtake_params_file, {'use_sim_time': use_sim_time}],
    )

    lead_selector_node = Node(
        package='venom_overtake_manager',
        executable='lead_selector_node',
        name='lead_selector_node',
        output='screen',
        parameters=[overtake_params_file, {'use_sim_time': use_sim_time}],
    )

    overtake_manager_node = Node(
        package='venom_overtake_manager',
        executable='overtake_manager_node',
        name='overtake_manager_node',
        output='screen',
        parameters=[overtake_params_file, {'use_sim_time': use_sim_time}],
    )

    mission_node = Node(
        package='venom_bringup',
        executable='craic_mission_main',
        name='craic_mission_main',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'road_network_file': road_network_file,
            'route_name': route_name,
            'coordinate_mode': 'cartesian_m',
            'pose_tracking_topic': '/Odometry',
            'cmd_vel_topic': '/cmd_vel',
            'waypoint_frame_id': 'map',
            'use_first_waypoint_as_origin': False,
            'require_map_topic': True,
            'require_pose_topic': True,
            'require_tf_ready': True,
        }],
    )

    delayed_mission_node = TimerAction(
        period=mission_start_delay_sec,
        actions=[mission_node],
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('world', default_value='RMUL'),
        DeclareLaunchArgument('dynamic_obstacles', default_value='true'),
        DeclareLaunchArgument('lio', default_value='fast_lio'),
        DeclareLaunchArgument('localization', default_value='slam_toolbox'),
        DeclareLaunchArgument('nav_rviz', default_value='true'),
        DeclareLaunchArgument('lio_rviz', default_value='false'),
        DeclareLaunchArgument(
            'road_network_file',
            default_value=os.path.join(
                venom_bringup_dir,
                'config',
                'scout_mini',
                'overtake_sim_road_network.yaml',
            ),
        ),
        DeclareLaunchArgument('route_name', default_value='main_lane_overtake_left'),
        DeclareLaunchArgument('mission_start_delay_sec', default_value='8.0'),
        DeclareLaunchArgument(
            'overtake_params_file',
            default_value=os.path.join(
                overtake_dir,
                'config',
                'overtake_manager_sim.yaml',
            ),
        ),
        sim_nav_launch,
        tracker_node,
        lead_selector_node,
        overtake_manager_node,
        delayed_mission_node,
    ])
