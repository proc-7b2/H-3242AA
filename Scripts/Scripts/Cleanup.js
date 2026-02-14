const { execSync } = require("child_process");
const { Octokit } = require("@octokit/rest");
const fs = require("fs");
const path = require("path");

const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
const modelId = process.env.MODEL_ID;
const objPath = process.env.OBJ_FILE_PATH; // From YML

async function run() {
    console.log(`🚀 Starting Headless Ant Pipeline for: ${modelId}`);

    try {
        // 1. RUN BLENDER PROCESS
        const outputPath = `output/${modelId}_cleaned.obj`;
        console.log(`🎨 Running Blender on: ${objPath}`);
        
        // Command to run Blender in background
        const blenderCmd = `blender -b -P Scripts/BlenderProc.py -- ${objPath} ${outputPath}`;
        execSync(blenderCmd, { stdio: 'inherit' });

        // 2. CLEANUP GITHUB INPUT FOLDER
        console.log(`🧹 Cleaning up input folder: input/${modelId}`);
        await deleteFolderRecursive(`input/${modelId}`);
        
        console.log("✅ Pipeline Complete!");
    } catch (error) {
        console.error("❌ Pipeline Failed:", error.message);
        process.exit(1);
    }
}

async function deleteFolderRecursive(repoPath) {
    const [owner, repo] = [process.env.REPO_OWNER, process.env.REPO_NAME];
    const { data: files } = await octokit.repos.getContent({ owner, repo, path: repoPath });

    for (const file of files) {
        if (file.type === "dir") {
            await deleteFolderRecursive(file.path);
        } else {
            await octokit.repos.deleteFile({
                owner, repo, path: file.path,
                message: `Cleanup: ${modelId} processed`,
                sha: file.sha
            });
        }
    }
}

run();
