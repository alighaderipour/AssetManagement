import jalaali from 'jalaali-js'

export function toJalali(dateString) {
  const date = new Date(dateString)
  const j = jalaali.toJalaali(date)
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${j.jy}/${j.jm.toString().padStart(2, '0')}/${j.jd.toString().padStart(2, '0')} ${hours}:${minutes}`
}
