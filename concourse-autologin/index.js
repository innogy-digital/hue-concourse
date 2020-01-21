const puppeteer = require('puppeteer');
var schedule = require('node-schedule');


const URL = "http://ci.lab.innogize.io/hd";
const USERNAME = "viewer";
const PASSWORD = "XXXX";

class ConcourseAutologin {
    async open() {
        this.browser = await puppeteer.launch({
            headless: false,
            args: ['--kiosk', '--disable-infobars']

        });
        this.page = await this.browser.newPage();
        await this.page.setViewport({width: 1920, height: 1080});
        await this.page.goto(URL);
    }

    async login() {
        await this.page.goto(URL);
        try {
            const loginButton = await this.page.waitForSelector("#login-item", {timeout: 1000});
            console.log("Try to login...");

            await loginButton.click();

            const loginLocalButton = await this.page.waitForSelector("button.dex-btn .dex-btn-icon--local", {timeout: 1000});
            await loginLocalButton.click();

            const loginInput = await this.page.waitForSelector("input#login", {timeout: 1000});
            const passwordInput = await this.page.waitForSelector("input#password", {timeout: 1000});
            const buttonLogin = await this.page.waitForSelector("button#submit-login", {timeout: 1000});

            await loginInput.type(USERNAME, {delay: 100});
            await passwordInput.type(PASSWORD, {delay: 100});
            await buttonLogin.click();
        } catch (e) {
            console.log("No need to login...");
        }
    }
}

(async () => {

    const autologin = new ConcourseAutologin();
    await autologin.open();
    await autologin.login();

    schedule.scheduleJob({minutes: 42}, async () => {
        await autologin.login();
    });
})();
