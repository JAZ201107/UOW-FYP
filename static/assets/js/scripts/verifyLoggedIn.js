import { StaticVar } from "./static.js"

const token = localStorage.getItem('token')
if (token === null){
    Swal.fire("User session expired. Please log in again.")
    window.location.replace(`${StaticVar.BASE_URL}`)
}
else {
    const verifyTokenEndpoint = `${StaticVar.BASE_URL}/api/verifytoken`
    const options = {
        method : "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Token ${token}`
            }
    }

    fetch(verifyTokenEndpoint, options)
    .then(response=>{
        if (!response.ok){
            Swal.fire("User session expired. Please log in again.")
            window.location.replace(`${StaticVar.BASE_URL}`)
        }
    })
}
    