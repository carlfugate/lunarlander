#!/usr/bin/env python3
"""Analyze bot log files for post-mortem debugging"""
import json
import sys

def analyze_log(log_file):
    frames = []
    with open(log_file) as f:
        for line in f:
            frames.append(json.loads(line))
    
    if not frames:
        print("Empty log file")
        return
    
    last = frames[-1]
    print(f"\n=== Bot Run Analysis ===")
    print(f"Total frames: {len(frames)}")
    print(f"Outcome: {last['reason']}")
    print(f"Final altitude: {last['altitude']:.1f}m")
    print(f"Final speed: {last['speed']:.1f} m/s")
    print(f"Final angle: {last['angle']:.1f}°")
    print(f"Fuel remaining: {last['fuel']:.0f}")
    print(f"Over landing zone: {last.get('is_over_zone', 'N/A')}")
    print(f"Safe speed: {last.get('is_safe_speed', 'N/A')}")
    print(f"Safe angle: {last.get('is_safe_angle', 'N/A')}")
    
    # Find critical moments
    print(f"\n=== Critical Moments ===")
    
    # Last 10 frames
    print(f"\nLast 10 frames before {last['reason']}:")
    for frame in frames[-10:]:
        actions_str = ", ".join(frame['actions']) if frame['actions'] else frame['reason']
        zone_str = "✓" if frame.get('is_over_zone') else "✗"
        print(f"  Frame {frame['frame']:3d}: Alt={frame['altitude']:5.1f}m Speed={frame['speed']:4.1f} "
              f"Angle={frame['angle']:5.1f}° Zone={zone_str} → {actions_str}")
    
    # High speed moments
    high_speed = [f for f in frames if f['speed'] > 8.0 and f['altitude'] < 200]
    if high_speed:
        print(f"\n⚠️  High speed warnings ({len(high_speed)} frames):")
        for frame in high_speed[:5]:
            print(f"  Frame {frame['frame']:3d}: Alt={frame['altitude']:5.1f}m Speed={frame['speed']:4.1f}")
    
    # High angle moments
    high_angle = [f for f in frames if abs(f['angle']) > 20]
    if high_angle:
        print(f"\n⚠️  High angle warnings ({len(high_angle)} frames):")
        for frame in high_angle[:5]:
            print(f"  Frame {frame['frame']:3d}: Alt={frame['altitude']:5.1f}m Angle={frame['angle']:5.1f}°")
    
    # Off-target moments
    off_target = [f for f in frames if not f.get('is_over_zone') and f['altitude'] < 100]
    if off_target:
        print(f"\n⚠️  Off-target at low altitude ({len(off_target)} frames):")
        for frame in off_target[:5]:
            x_err = frame['zone_x'] - frame['x']
            print(f"  Frame {frame['frame']:3d}: Alt={frame['altitude']:5.1f}m X-error={x_err:.1f}m")
    
    # Statistics
    print(f"\n=== Statistics ===")
    avg_speed = sum(f['speed'] for f in frames) / len(frames)
    max_speed = max(f['speed'] for f in frames)
    print(f"Average speed: {avg_speed:.1f} m/s")
    print(f"Max speed: {max_speed:.1f} m/s")
    
    thrust_frames = sum(1 for f in frames if 'thrust_on' in f.get('actions', []))
    print(f"Thrust usage: {thrust_frames}/{len(frames)} frames ({thrust_frames/len(frames)*100:.1f}%)")
    
    over_zone_frames = sum(1 for f in frames if f.get('is_over_zone'))
    print(f"Over landing zone: {over_zone_frames}/{len(frames)} frames ({over_zone_frames/len(frames)*100:.1f}%)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_log.py <log_file.jsonl>")
        sys.exit(1)
    
    analyze_log(sys.argv[1])
