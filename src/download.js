function table_to_csv(source) {
    const columns = Object.keys(source.data)
    const nrows = source.get_length()
    const lines = [columns.join(',')]

    for (let i = 0; i < nrows; i++) {
        let row = [];
        for (let j = 0; j < columns.length; j++) {
            const column = columns[j]
            row.push(source.data[column][i].toString())
        }
        lines.push(row.join(','))
    }
    return lines.join('\n').concat('\n')
}

// Get datestring for filename
var today = new Date();
var dd = today.getDate();
var mm = today.getMonth()+1; //January is 0!
var yyyy = today.getFullYear();
var MM = today.getMinutes();
var HH = today.getHours();

if(dd<10) {
    dd = '0'+dd
} 

if(mm<10) {
    mm = '0'+mm
} 
if (MM<10){
    MM = '0'+MM
}
if (HH<10){
    HH = '0'+HH
}
var filename = yyyy + '-' + mm + '-' + dd + '_' + HH + '-' + MM + '_bandotuner.csv'



//const filename = 'data_result.csv'
filetext = table_to_csv(source)
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