FROM --platform=linux/amd64 nvidia/cuda:11.8.0-base-ubuntu20.04

# Prevent timezone prompt
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and Python
RUN apt-get update && apt-get install -y \
  python3 \
  python3-pip \
  libgl1-mesa-glx \
  libglib2.0-0 \
  && rm -rf /var/lib/apt/lists/*

# Create symlink for python
RUN ln -s /usr/bin/python3 /usr/local/bin/python

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Download YOLOv8 weights during build
RUN python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
# CMD ["python3", "src/main.py", "--video_url", "Ref::video_url", "--callback_url", "Ref::callback_url"]
# CMD defined in the job definition

# https://yolo-batch.s3.us-east-1.amazonaws.com/dogs.mp4?response-content-disposition=inline&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEKL%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIQCN5hSZZ%2B1xwdZBuMURaXVK77GDedaWv9ReVWTIfWzWzgIgcg92KL21M9%2Fk%2Fmqmdrx4d8TabcchEe%2BJ42VdTZ4eQJ0q5wMI2%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAEGgw2Mzc3NTkxMzE0MjQiDElXT8wdaKTmd%2B%2FW0iq7A1upM4HOuv8%2BdZtSl91q1m5e%2B6Zf9f7KU0ka4Dx6SytlDBiZe%2BJIyHL0ZksFIHDhOuU2RKnZ7KEB9P88%2BgNIatBKe5nEd9jPPkCoIQldnneWaHDY595mD5W49EPm4xVWw8b8LEHtOll4oYl%2B63kfkyjDjex5pK%2F%2FlzvPwDlv6ig7VnwJ0ysdULpCosZF7kwaC%2By6DxIDp%2Bt8G6CtdZTFosl1pKL%2BjHP7A6lfbzY1zGPnb3nZNd1%2FOBzOUHIdXFigZVEDQeAWO0QO2t8MGs6N46gyHPQ8g9UJTeHU4ONIEWK23aT4iJkpxdyk%2FGX0sK3pYNdKNdYRZbNxX399NUucEeyKqnqr8qsWTXNd86ma0gr8wcAY9Ht5GFOkEIF8JzL6UKvPucyvaDDRollLNEGq%2B5LAJ2H8hh00MXl0INrF2hbRyeg4GcGEs1UylV1LU5UXUEj9DmQ1gpLgN2GpHegXewvnGujbOOnMHe3aB6CiMXH0oMeQl8frNlGLedAo%2ByO%2BsFCbjcDbrGVrdso8vxSc3us3NHKRMJRyRXriQ2nMQBN7aN0DUFinQ7OuMF1S0JnvR1GCdtnbwOUfqMDRML2Kl74GOuQCAk2zi2yQiBqROTbZ855buUlsItCF7N0egeNqYkJND%2FgkOwanQBIa48Bp2vrg0zfbXSWX8CngNBUinJdv3TTcC1ACRFtxa9ZmU0IlBVPpjEE4iGLfIs8dMV%2BPSwip21BOv%2F6jjgYCEo8IY%2BdtUgByUZTYlA67WO93eqVYgEjCZas1cp7YWu%2B945%2BaQJ3IVjraP8lH3Q%2Bk1N7PI2Uu0vRqj451EYFmCDQDPOr8YJnX%2By%2F6GHpXBPVyC%2B5WrSVEueFGQNU2A3J0%2BVsGO1%2FhRQAHM4utfF6GQ8FdqEx6jKcP4X%2FNaaOhohKUik9h7EqCF1Gy%2FZoyti25sNZVIIItnOqJPhDhfkTdJ%2B95Ze0YgTHk6uSohFgme1rPXzaHQXVpRrunFfshW3KLwygM8WSn%2BRWQS7YkYebMfEn3EgnglKgIMm3lkr8Se%2FsEwFFxC%2B5ekrKYIPOuMPJofBTo5ZscJUq4R%2BmBNOM%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAZI7LIB4QOFSNUPSX%2F20250303%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250303T174436Z&X-Amz-Expires=18000&X-Amz-SignedHeaders=host&X-Amz-Signature=81d218a9a58f1e4803b83ac9f24965524699ee7d549e7316514f00500e74971d