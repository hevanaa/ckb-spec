%undefine _debugsource_packages

Name:           ckb-next
Version:        0.3.0
Release:        1%{?dist}
Summary:        Corsair RGB keyboard driver for Linux and OS X
Group:          Applications/System
License:        GPLv2
URL:            https://github.com/ckb-next/ckb-next
Source0:        https://github.com/ckb-next/ckb-next/archive/master.tar.gz#/%{name}-%{version}.tar.gz

# Upstream provides none of the following files
Source1:        ckb-next.appdata.xml
Source2:        ckb-next.1
Source3:        99-ckb-next.preset

BuildRequires:  cmake
BuildRequires:  qt5-qtbase-devel >= 5.2.0
%if 0%{?fedora}
BuildRequires:  quazip-qt5-devel
BuildRequires:  libgudev-devel
%endif
%if 0%{?rhel}
BuildRequires:  quazip-devel
BuildRequires:  libgudev1-devel
%endif
BuildRequires:  libappindicator-devel
BuildRequires:  systemd-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  zlib-devel
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
%{?systemd_requires}

Requires:       qt5-qtbase >= 5.2.0
Requires:       qt5ct
Obsoletes:      ckb

%description
ckb-next is an open-source driver for Corsair keyboards and mice. It aims to
bring the features of their proprietary CUE software to the Linux and Mac
operating systems. This project is currently a work in progress, but it already
supports much of the same functionality, including full RGB animations.

%prep
%setup -q -n ckb-next-%{version}
# Correct dir for animations
sed -e 's|"/usr/lib"|"%{_libdir}"|' -i src/gui/animscript.cpp
# Fedora uses /usr/libexec for daemons
sed -e '/^ExecStart/cExecStart=%{_libexecdir}/ckb-next-daemon' -i linux/systemd/ckb-next-daemon.service.in

%build
%cmake -H. -Bbuild -DCMAKE_BUILD_TYPE=Release -DSAFE_INSTALL=OFF -DSAFE_UNINSTALL=OFF
%cmake --build build --target all -- -j build
cd build
%make_build
cd ..

# Color freeze fix
sed -e 's|^Exec=/usr/bin/ckb-next|Exec=env QT_QPA_PLATFORMTHEME=qt5ct /usr/bin/ckb-next|' -i build/src/gui/ckb-next.desktop

%install
install -m 644 -D linux/udev/99-ckb-daemon.rules %{buildroot}%{_udevrulesdir}/99-ckb-daemon.rules
install -D -m 755 build/bin/ckb-next %{buildroot}%{_bindir}/ckb-next
install -D -m 755 build/bin/ckb-next-daemon %{buildroot}%{_libexecdir}/ckb-next-daemon
install -d %{buildroot}%{_libdir}/ckb-next-animations
install -D -m 755 build/bin/gradient %{buildroot}%{_libdir}/ckb-next-animations/gradient
install -D -m 755 build/bin/heat %{buildroot}%{_libdir}/ckb-next-animations/heat
install -D -m 755 build/bin/mviz %{buildroot}%{_libdir}/ckb-next-animations/mviz
install -D -m 755 build/bin/pinwheel %{buildroot}%{_libdir}/ckb-next-animations/pinwheel
install -D -m 755 build/bin/rain %{buildroot}%{_libdir}/ckb-next-animations/rain
install -D -m 755 build/bin/random %{buildroot}%{_libdir}/ckb-next-animations/random
install -D -m 755 build/bin/ripple %{buildroot}%{_libdir}/ckb-next-animations/ripple
install -D -m 755 build/bin/wave %{buildroot}%{_libdir}/ckb-next-animations/wave
install -D -m 755 build/lib/libKissFFT.so %{buildroot}%{_libdir}/libKissFFT.so
install -m 644 -D build/src/gui/ckb-next.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/ckb-next.png
install -Dpm 0644 %{SOURCE3} %{buildroot}/%{_presetdir}/99-ckb-next.preset
install -m 644 -D linux/systemd/ckb-next-daemon.service.in %{buildroot}%{_unitdir}/ckb-next-daemon.service
desktop-file-install --dir=%{buildroot}%{_datadir}/applications build/src/gui/ckb-next.desktop
install -Dpm 0644                                                             \
%{SOURCE1} %{buildroot}%{_datadir}/appdata/ckb-next.appdata.xml
appstream-util                                                                \
validate-relax --nonet %{buildroot}%{_datadir}/appdata/ckb-next.appdata.xml
install -Dpm 0644 %{SOURCE2} %{buildroot}%{_mandir}/man1/ckb-next.1

%post
%systemd_post ckb-next-daemon.service
if [ $1 -eq 1 ]; then
    # starting daemon also at install
    systemctl start ckb-next-daemon.service >/dev/null 2>&1 || :
    touch --no-create %{_datadir}/icons/hicolor >&/dev/null || :
fi
udevadm control --reload-rules 2>&1 > /dev/null || :

%preun
%systemd_preun ckb-next-daemon.service

%postun
%systemd_postun_with_restart ckb-next-daemon.service
if [ $1 -eq 0 ]; then
    touch --no-create %{_datadir}/icons/hicolor >&/dev/null || :
    gtk-update-icon-cache %{_datadir}/icons/hicolor >&/dev/null || :
fi
udevadm control --reload-rules 2>&1 > /dev/null || :

%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :


%files
%defattr(-,root,root)
%license LICENSE
%doc CHANGELOG.md FIRMWARE README.md ROADMAP.md
%{_udevrulesdir}/*.rules
%{_bindir}/ckb-next
%{_libexecdir}/ckb-next-daemon
%{_libdir}/libKissFFT.so
%{_libdir}/ckb-next-animations
%{_unitdir}/ckb-next-daemon.service
%{_presetdir}/99-ckb-next.preset
%{_datadir}/applications/ckb-next.desktop
%{_datadir}/appdata/ckb-next.appdata.xml
%{_datadir}/icons/hicolor/*/apps/ckb-next.png
%{_mandir}/man1/ckb-next.1*

%changelog
* Fri Jun 15 2018 Johan Heikkila <johan.heikkila@gmail.com> - 0.3.0:1
- Update to 0.3.0 release
- set QT_QPA_PLATFORMTHEME only for binary
* Mon Jan 22 2018 Johan Heikkila <johan.heikkila@gmail.com> - 0.2.9:0.1.20180122git2316518
- Update to latest snapshot.
* Sun Dec 17 2017 Johan Heikkila <johan.heikkila@gmail.com> - 0.2.8:0.9.20171217git142b307
- Update to latest snapshot.
- Disable debugsource due to build error with empty file debugsourcefiles.list.
* Fri Nov 17 2017 Johan Heikkila <johan.heikkila@gmail.com> - 0.2.8:0.8.20171111gitb88d8be
- Update to latest snapshot.
* Fri Oct 20 2017 Johan Heikkila <johan.heikkila@gmail.com> - 0.2.8:0.7.20171014gitda28864
- Update to latest snapshot.
* Sun Aug 20 2017 Johan Heikkila <johan.heikkila@gmail.com> - 0.2.8:0.6.20170820git6af2773
- Update to latest snapshot.
* Wed Jul 26 2017 Johan Heikkila <johan.heikkila@gmail.com> - 0.2.8:0.5.20170726git9dc8216
- Update to latest snapshot.
- Color change freeze workaround by requiring qt5ct and adding to environment.
* Fri Jul 07 2017 Johan Heikkila <johan.heikkila@gmail.com> - 0.2.8:0.4.20170707git1331253
- Update to latest snapshot.
* Fri Jun 23 2017 Johan Heikkila <johan.heikkila@gmail.com> - 0.2.8:0.3.20170621gitae7346b
- Update to latest snapshot.
* Thu May 25 2017 Johan Heikkila <johan.heikkila@gmail.com> - 0.2.8:0.2.20170525gite54c911
- Fix animation path.
- Update to latest snapshot.
* Thu May 18 2017 Johan Heikkila <johan.heikkila@gmail.com> - 0.2.8:0.1.20170518git5a34841
- Update to 0.2.8 latest snapshot.
* Fri Apr 14 2017 Johan Heikkila <johan.heikkila@gmail.com> - 0.2.7:0.7.20170414git565add5
- Added systemd preset.
- Update to latest snapshot.
* Sun Feb 19 2017 Johan Heikkila <johan.heikkila@gmail.com> - 0.2.7:0.6.20170219gitb59d179
- Changed package name to ckb-next.
- Update to latest snapshot.
* Sun Jan 22 2017 Johan Heikkila <johan.heikkila@gmail.com> - 0.2.7:0.2.20170120git89e8750
- Update to latest snapshot.
* Thu Dec 1 2016 Johan Heikkila <johan.heikkila@gmail.com> - 0.2.6:0.1
- Created spec file for Fedora based on the Suse spec file
- added appdata file
- added man page
* Thu Aug 25 2016 - aloisio@gmx.com
- Update to version 0.2.6
- Use external quazip only when available
- Replaced ckb-fix-desktop-file.patch with %suse_update_desktop_file
- Replaced ckb-daemon-path.patch and ckb-animations-path.patch with macros \
  for consistency.
* Sun Apr 17 2016 - herbert@graeber-clan.de
- Add hicolor folder, too
* Sun Apr 17 2016 - herbert@graeber-clan.de
- Fix icon folder
* Fri Apr 15 2016 - herbert@graeber-clan.de
- Initial package
- Use /var/run instead of /dev/input for communication with the daemon.
- move the daemon and the animations into the libexec folder
