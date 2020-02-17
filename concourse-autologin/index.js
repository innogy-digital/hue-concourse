const puppeteer = require('puppeteer-core');
const schedule = require('node-schedule');


const PROJECT_DASHBOARD_URL = 'https://dlab-project-dashboard.cfapps.mila.external.ap.innogy.com/';
const CONCOURSE_URL = "http://ci.lab.innogize.io/hd";


async function concourseLoginCallback(page) {
    const username = process.env.CONCOURSE_USERNAME;
    const password = process.env.CONCOURSE_PASSWORD;

    if (!username || !password) {
        console.error('ERROR - Can\'t Login! ' +
            'Please set environment variables "CONCOURSE_USERNAME" and "CONCOURSE_PASSWORD"!');
        return;
    }

    try {
        await page.reload();

        const loginButton = await page.waitForSelector("#login-item", {timeout: 2000});
        console.log("Try to login...");

        await loginButton.click();

        const loginLocalButton = await page.waitForSelector("button.dex-btn .dex-btn-icon--local", {timeout: 2000});
        await loginLocalButton.click();

        const loginInput = await page.waitForSelector("input#login", {timeout: 2000});
        const passwordInput = await page.waitForSelector("input#password", {timeout: 2000});
        const buttonLogin = await page.waitForSelector("button#submit-login", {timeout: 2000});

        await loginInput.type(username, {delay: 100});
        await passwordInput.type(password, {delay: 100});
        await buttonLogin.click();
    } catch (e) {
        console.log("No need to login...");
    }
}

async function dashboardCallback(page) {
    await page.reload();
}


class ConcourseAutologin {
    constructor() {
        this.pages = [];
        this.activePage;
    }

    async launch() {
        this.browser = await puppeteer.launch({
            headless: false,
            args: [
                '--kiosk',
                '--disable-infobars',
                '--no-sandbox'
            ],
            executablePath: 'chromium-browser'
        });
    }

    async addPage(url, loginCallback) {
        const page = await this.browser.newPage();
        await page.setViewport({width: 1920, height: 1080});
        await page.goto(url);

        if (loginCallback) {
            await loginCallback(page);
        }

        this.pages.push({
            page: page,
            url: url,
            callback: loginCallback
        });
        this.activePage = page;
    }

    async nextPage() {
        let i = this.pages.indexOf(this.activePage) + 1;
        if (i >= this.pages.length) {
            i = 0;
        }

        this.activePage = this.pages[i];
        await this.activePage.page.bringToFront();
        if (this.activePage.callback) {
            await this.activePage.callback(this.activePage.page);
        }
    }
}

(async () => {
    const autologin = await new ConcourseAutologin();
    await autologin.launch();

    await autologin.addPage(CONCOURSE_URL, concourseLoginCallback);
    await autologin.addPage(PROJECT_DASHBOARD_URL, dashboardCallback);

    schedule.scheduleJob({rule: '0 */1 * * * *'}, async () => {
        await autologin.nextPage();
    });
})();
