function table_to_csv(source, number) {
    const columns = Object.keys(source.data)

    const lines = [columns.join(',')]
    for (let i = 0; i < number; i++) {
        let row = [];
        for (let j = 0; j < columns.length; j++) {
            const column = columns[j]
            row.push(source.data[column][i].toString())
        }
        lines.push(row.join(','))
    }
    return lines.join('\n').concat('\n')
}

console.log('Dowloading formatted csv')
const number = (cb_obj)['origin']['tags'][0]
const test = (cb_obj)['origin']['tags'][1]
const mof = (cb_obj)['origin']['tags'][2]

const filename = mof + '_adsorption_data.csv'
const filetext = table_to_csv(test, number)
const blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' })

//addresses IE
if (navigator.msSaveBlob) {
    navigator.msSaveBlob(blob, filename)
} else {
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename
    link.target = '_blank'
    link.style.visibility = 'hidden'
    link.dispatchEvent(new MouseEvent('click'))
}