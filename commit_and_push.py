import subprocess

def main():
    # Copy the file to root level
    subprocess.run(['cp', 'data/new_data/new_data.csv', 'new_data.csv'])

    # Set Git configuration
    subprocess.run(['git', 'config', '--global', 'user.name', 'Mihran Dovlatyan'])
    subprocess.run(['git', 'config', '--global', 'user.email', 'mihrandovlatyan@gmail.com'])

    # Stage files
    subprocess.run(['git', 'add', 'data/new_data/new_data.csv'])
    subprocess.run(['git', 'add', 'new_data.csv'])

    # Commit changes
    subprocess.run(['git', 'commit', '-m', 'Add simulated new_data.csv for retraining'])

    # Show commit details for debugging
    subprocess.run(['git', 'show', '--stat', 'HEAD'])

    # Push to remote branch
    subprocess.run(['git', 'push', 'origin', 'retrain-the-model'])

if __name__ == '__main__':
    main()
