import { StaticVar } from "./static.js"

const loginForm = document.getElementById('loginForm')
if (loginForm) {
    loginForm.addEventListener('submit', handleLogin)
}
const messagePara = document.getElementById('message')

function setMessage(message) {
    messagePara.textContent = message
}

function handleLogin(event) {
    event.preventDefault()

    const loginEndpoint = `${StaticVar.BASE_URL}/api/loginuser/`
    let loginFormData = new FormData(loginForm)
    let loginObjectData = Object.fromEntries(loginFormData)
    let bodyStr = JSON.stringify(loginObjectData)

    const options = {
        method : "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: bodyStr
    }

    fetch(loginEndpoint, options)
    .then(response=>{
        if (response.ok){
        return response.json()
        }
        throw new Error("Invalid credentials entered")
    })
    .then(data=>{
        // Successful login
        // Store token in localstorage
        // Redirect user to home page
        localStorage.setItem('token', data.token)
        if (data.admin == true)
            window.location.replace(`${StaticVar.BASE_URL}/sys_admin_home/`)
        else
            window.location.replace(`${StaticVar.BASE_URL}/user/home`)
    })
    .catch(err =>{
        loginForm.reset()
        setMessage(err.message);
    })
}