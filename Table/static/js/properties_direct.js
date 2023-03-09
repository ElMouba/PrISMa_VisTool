const mof_name = (cb_obj)['origin']['tags'][0]

console.log(mof_name)

window.open('http://localhost:5006/new_page?name=' + mof_name)