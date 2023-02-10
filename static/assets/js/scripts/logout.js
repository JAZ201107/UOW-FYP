import { StaticVar } from "./static.js"

const logoutButton = document.getElementById('logoutbtn')
if (logoutButton) {
    logoutButton.addEventListener('click', handleLogout)
}

function handleLogout(event) {
    event.preventDefault()

    const logoutEndpoint = `${StaticVar.BASE_URL}/api/logout/`
    const token = localStorage.getItem('token')

    if (token != null) {
        const options = {
            method : "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Token ${token}`
            }
        }

    fetch(logoutEndpoint, options)
    .then(response=>{
        if (response.ok){
            console.log("Logout Successful")
        }
    })

    localStorage.removeItem('token')
    }

    window.location.replace(`${StaticVar.BASE_URL}`)
}