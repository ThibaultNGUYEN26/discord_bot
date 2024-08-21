# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Install ffmpeg for voice channel support
RUN apt-get update && apt-get install -y ffmpeg

# Ensure the .pem file has the correct permissions
RUN chmod 400 discord_bot_key.pem

# Set environment variables if needed (e.g., for Discord token)
# ENV DISCORD_TOKEN=your_token_here

# Run the bot using the command in the Makefile
CMD ["make", "run"]
