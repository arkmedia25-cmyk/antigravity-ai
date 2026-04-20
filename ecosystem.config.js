module.exports = {
  apps: [
    {
      name: "my_ai_ark_agent_bot",
      script: "/root/antigravity-ai/venv/bin/python",
      args: "-u src/interfaces/telegram/handler.py",
      interpreter: "none",
      cwd: "/root/antigravity-ai",
      env: {
        PYTHONPATH: "/root/antigravity-ai",
        PYTHONUNBUFFERED: "1"
      },
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 2000
    }
  ]
};
