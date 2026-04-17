# Venom Nav Simulation

`Venom Nav Simulation` is a standalone ROS 2 simulation workspace for small mobile robot navigation with a simulated Livox MID-360 and IMU.

This project is intended to serve two goals:

1. Provide a fast testbed for `MID360 + LIO + Nav2` validation before touching real hardware.
2. Become the long-term simulation baseline that can later be split out into its own GitHub repository.

The current bootstrap is intentionally pragmatic: the initial package layout is imported from `pb_rm_simulation` so the simulation chain can be studied and iterated quickly. The first round of cleanup has already replaced the outer simulation package with the project-owned `venom_mid360_simulation` package, while keeping the rest of the internal `rm_*` packages stable to reduce migration risk.

## Scope

- Gazebo-based small vehicle simulation
- Simulated `Livox MID-360` point cloud output
- Simulated IMU output
- LIO validation with `Fast-LIO` or `Point-LIO`
- Navigation validation with `Nav2`
- RM-style map and world testing

## What This Repository Can Do

- Run a small mobile robot in Gazebo Classic with a simulated MID-360 and IMU.
- Publish `livox_ros_driver2/msg/CustomMsg`, `sensor_msgs/msg/PointCloud2`, `sensor_msgs/msg/Imu`, and `geometry_msgs/msg/Twist`-driven chassis motion topics for integration testing.
- Validate both `Fast-LIO` and `Point-LIO` against the simulated sensor stream.
- Convert simulated point clouds into `LaserScan` for 2D navigation workflows.
- Run `Nav2` in mapping mode and known-map navigation mode.
- Test multiple localization strategies in navigation mode: `slam_toolbox`, `AMCL`, and `ICP`.
- Use RM competition-style maps and worlds as repeatable regression environments.
- Serve as a staging workspace for future alignment with the main `venom_vnv` bringup architecture.

## Main Packages

- `venom_mid360_simulation`: Gazebo world loading, robot spawning, simulation assets, and MID-360 simulation carrier package.
- `rm_nav_bringup`: high-level launch entry for simulation and real-robot navigation experiments.
- `rm_navigation`: Nav2-facing launch and navigation integration helpers.
- `rm_localization/icp_registration`: optional ICP-based global pose initialization.
- `rm_perception/*`: IMU filtering, ground segmentation, and pointcloud-to-laserscan conversion utilities.
- `rm_simulation/livox_laser_simulation_RO2`: Livox MID-360 simulation plugin implementation used by the imported baseline.

## Supported Workflows

### 1. Simulation Mapping

Use Gazebo to drive the robot in an unknown map while building the navigation map online.

Typical chain:

- Gazebo world
- simulated MID-360 + IMU
- `Fast-LIO` or `Point-LIO`
- ground segmentation
- pointcloud to laserscan
- `slam_toolbox` mapping
- `Nav2`

### 2. Simulation Navigation With Known Map

Use a prepared map and PCD to test global navigation behavior in a repeatable environment.

Localization options:

- `slam_toolbox`
- `AMCL`
- `ICP`

### 3. Real-Robot Bringup Baseline

The workspace also contains a real-hardware bringup path in `rm_nav_bringup/launch/bringup_real.launch.py`. Its value here is not that this repository is hardware-first, but that the simulation and real pipelines share similar LIO and navigation composition, which makes Sim2Real iteration easier.

### 4. Algorithm Regression

Because the repository bundles fixed worlds, maps, and configuration sets, it can be used as a regression harness for:

- LIO parameter tuning
- localization comparisons
- Nav2 behavior tuning
- scan generation parameter tuning
- TF and frame-convention validation

## Current Identity Boundary

This is the first cleanup stage.

- `pb_*` naming has been removed from the runtime package layer.
- The main simulation package is now `venom_mid360_simulation`.
- Internal `rm_*` package names are intentionally kept for stability in this round.
- A later stage can rename `rm_*` packages once the launch and dependency graph are fully under test.

## Current Layout

```text
simulation/venom_nav_simulation/
├── src/rm_nav_bringup
├── src/rm_navigation
├── src/rm_localization
├── src/rm_perception
└── src/rm_simulation/venom_mid360_simulation
```

## Quick Start

```bash
cd simulation/venom_nav_simulation
rosdep install -r --from-paths src --ignore-src --rosdistro $ROS_DISTRO -y
colcon build --symlink-install
source install/setup.bash
ros2 launch rm_nav_bringup bringup_sim.launch.py \
  world:=RMUL \
  mode:=nav \
  lio:=pointlio \
  localization:=slam_toolbox \
  lio_rviz:=False \
  nav_rviz:=True
```

The imported baseline targets `Ubuntu 22.04 + ROS 2 Humble + Gazebo Classic`. A later refactor can move this workspace to a cleaner `simulation/launch`, `simulation/worlds`, `simulation/models`, and `simulation/config` structure, or migrate to modern Gazebo if needed.

## Why This Exists

The main `venom_vnv` workspace currently lacks a dedicated simulation area for navigation testing. This subproject is added as a staging area so simulation-specific assets do not continue to leak into bringup and hardware-oriented packages.

## Upstream Origin

This project is **not** a fork.

It is a new repository candidate bootstrapped from the ideas and file layout of:

- `pb_rm_simulation`: <https://github.com/LihanChen2004/pb_rm_simulation>

The imported baseline is used under the upstream `MIT` license retained in [LICENSE](/Users/liyh/venom_vnv/simulation/venom_nav_simulation/LICENSE).

## Acknowledgement

This subproject would not exist without the open work published by the original `pb_rm_simulation` authors and the upstream projects it integrates.

- Thanks to the authors of `pb_rm_simulation` for open-sourcing a complete `MID360 + Gazebo + LIO + Nav2` practice workspace.
- Thanks to `Livox-SDK/livox_laser_simulation` and related ROS 2 ports for the MID-360 simulation plugin direction.
- Thanks to the maintainers of `Fast-LIO`, `Point-LIO`, `slam_toolbox`, `Nav2`, and other upstream dependencies used by the reference project.

More detailed attribution notes are recorded in [ACKNOWLEDGEMENTS.md](/Users/liyh/venom_vnv/simulation/venom_nav_simulation/ACKNOWLEDGEMENTS.md).

## Planned Cleanup

1. Replace legacy `rm_*` package names with project-specific names.
2. Separate reusable simulation assets from RM competition maps.
3. Remove source-tree prebuilt artifacts and build plugins from source only.
4. Align topics and TFs with the `venom_vnv` bringup stack.
5. Add a cleaner top-level launch entry for `simulation + navigation + LIO`.
