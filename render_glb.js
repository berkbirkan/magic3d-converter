const puppeteer = require('puppeteer');

async function renderGLB(glbPath, pngPath) {
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    await page.goto(`file://${__dirname}/render.html`, { waitUntil: 'networkidle2' });

    // Set the GLB path
    await page.evaluate((glbPath) => {
        document.getElementById('glb-path').innerText = glbPath;
    }, glbPath);

    // Wait for the 3D model to load and render
    await page.waitForSelector('#render-complete');

    // Take screenshot
    await page.screenshot({ path: pngPath });

    await browser.close();
}

const glbPath = process.argv[2];
const pngPath = process.argv[3];

renderGLB(glbPath, pngPath).catch(console.error);
