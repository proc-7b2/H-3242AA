const { execSync } = require("child_process");
const { Octokit } = require("@octokit/rest");
const fs = require("fs");
const path = require("path");

const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
const modelId = process.env.MODEL_ID;
const objPath = process.env.OBJ_FILE_PATH;

async function run() {
    console.log(`🚀 Pipeline Started: ${modelId}`);

    try {
        // 1. Setup Output Folder Structure: output/CleanedFiles/[ID]/
        const outputDir = path.join('output', 'CleanedFiles', modelId);
        const outputFilePath = path.join(outputDir, `${modelId}.obj`);
        
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }

        // 2. RUN BLENDER
        console.log(`🎨 Processing: ${objPath}`);
        const blenderCmd = `blender -b -P Scripts/BlenderProc.py -- "${objPath}" "${outputFilePath}"`;
        execSync(blenderCmd, { stdio: 'inherit' });

        // 3. CLEANUP GITHUB INPUT
        console.log(`🧹 Cleaning up: input/${modelId}`);
        await deleteFolderRecursive(`input/${modelId}`);
        
        console.log(`✅ Success! File saved to: ${outputFilePath}`);
    } catch (error) {
        console.error("❌ Pipeline Failed:", error.message);
        process.exit(1);
    }
}

async function deleteFolderRecursive(repoPath) {
    const [owner, repo] = [process.env.REPO_OWNER, process.env.REPO_NAME];
    try {
        const { data: files } = await octokit.repos.getContent({ owner, repo, path: repoPath });

        for (const file of files) {
            if (file.type === "dir") {
                await deleteFolderRecursive(file.path);
            } else {
                await octokit.repos.deleteFile({
                    owner, repo,
                    path: file.path,
                    message: `Cleanup: ${modelId} processed`,
                    sha: file.sha
                });
            }
        }
    } catch (e) {
        console.log("Note: Folder already empty or deleted.");
    }
}

run();
