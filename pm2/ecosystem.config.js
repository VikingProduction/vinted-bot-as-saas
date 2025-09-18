module.exports = {
  apps: [
    {
      name: 'vinted-bot-api',
      script: 'venv/bin/uvicorn',
      args: 'backend.app.main:app --host 0.0.0.0 --port 8000',
      cwd: '.',
      instances: 2,
      exec_mode: 'cluster',
      env: { PYTHONPATH: process.cwd() },
      error_file: '/var/log/vinted-bot/api-error.log',
      out_file: '/var/log/vinted-bot/api-out.log',
      log_file: '/var/log/vinted-bot/api.log'
    },
    {
      name: 'vinted-bot-worker',
      script: 'venv/bin/celery',
      args: '-A backend.app.tasks.celery_app worker --loglevel=info --concurrency=4',
      cwd: '.',
      instances: 1,
      env: { PYTHONPATH: process.cwd() }
    },
    {
      name: 'vinted-bot-scraper',
      script: 'venv/bin/python',
      args: '-m backend.app.tasks.scraper',
      cwd: '.',
      instances: 1,
      autorestart: true,
      env: { PYTHONPATH: process.cwd() }
    }
  ]
}
