// SMS Mass Send - Installer
// Copy this entire script into Scriptable, run once, then delete this script

const SCRIPT_URL = "https://gist.githubusercontent.com/hugootth/606b8cd78ae42b0082b6152ba65094e7/raw/script.js";
const SCRIPT_NAME = "SMS Mass Send";

let req = new Request(SCRIPT_URL);
let code = await req.loadString();

let fm = FileManager.iCloud();
let path = fm.joinPath(fm.documentsDirectory(), SCRIPT_NAME + ".js");
fm.writeString(path, code);

let alert = new Alert();
alert.title = "✅ Installed!";
alert.message = "SMS Mass Send has been installed.\n\nYou can now delete this installer script.";
alert.addAction("OK");
await alert.present();
