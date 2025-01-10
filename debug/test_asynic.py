import asyncio

# Example asynchronous function
async def async_task(name, delay):
    print(f'Task {name} starting')
    await asyncio.sleep(delay)
    print(f'Task {name} completed')

async def run_async_tasks():
    # Schedule multiple tasks to run concurrently
    tasks = [
        asyncio.create_task(async_task('A', 2)),
        asyncio.create_task(async_task('B', 3)),
        asyncio.create_task(async_task('C', 1))
    ]
    # Optionally, you can wait for all tasks to complete
    await asyncio.gather(*tasks)

def main():
    # This is your main synchronous entry point
    print('Starting main program')
    asyncio.run(run_async_tasks())
    print('Main program continues after async tasks are scheduled')
    # Any code here would run after the async tasks have been started (and possibly completed)

if __name__ == '__main__':
    main()
