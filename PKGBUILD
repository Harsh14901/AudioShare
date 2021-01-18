# This is an example PKGBUILD file. Use this as a start to creating your own,
# and remove these comments. For more information, see 'man PKGBUILD'.
# NOTE: Please fill out the license field for your package! If it is unknown,
# then please put 'unknown'.

# Maintainer: Saptarshi <2001saptarshi@gmail.com>
pkgname=audioshare
pkgver=1.0.0
_foldername=$pkgname-linux-x64-$pkgver
pkgrel=1
pkgdesc="An audiosharing application from a single video source"
arch=('x86_64')
url="https://github.com/Harsh14901/CAV"
license=('MIT')
depends=(vlc ffmpeg)
makedepends=()
provides=(audioshare)
conflicts=(audioshare)
replaces=()
md5sums=('6afea0560ab51bef53beeeec0b2a0b3a')
backup=()
source=("${url}/releases/download/1.0/${_foldername}.zip")
noextract=()
package() {
	cd "${pkgname}-linux-x64"
	mkdir -p ${pkgdir}/usr/lib/
	mkdir -p  ${pkgdir}/usr/bin/ 
	mkdir -p ${pkgdir}/usr/share/applications/
	mkdir -p ${pkgdir}/usr/share/pixmaps/
	cp -r . ${pkgdir}/usr/lib/${pkgname}
	ln -s ${pkgdir}/usr/lib/${pkgname}/${pkgname} ${pkgdir}/usr/bin/${pkgname}
	cd resources/app/
	cp desktop/${pkgname}.desktop ${pkgdir}/usr/share/applications/
	cp icons/${pkgname}.png ${pkgdir}/usr/share/pixmaps/
}
