import os
import subprocess


def split_video(input_file, output_dir, segment_time="00:01:00"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    command = [
        "ffmpeg",
        "-i", input_file,
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0",
        "-segment_time", segment_time,
        "-f", "segment",
        os.path.join(output_dir, "vlog_%08d.mp4")
    ]

    subprocess.run(command, check=True)


if __name__ == "__main__":
    input_file = "videoplayback.mp4"
    output_dir = "videos"
    split_video(input_file, output_dir)
