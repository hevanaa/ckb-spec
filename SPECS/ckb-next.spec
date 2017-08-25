Name:           ckb-next
Version:        0.2.8
Release:        0.6.20170820git6af2773%{?dist}
Summary:        Corsair RGB keyboard driver for Linux and OS X
Group:          Applications/System
License:        GPLv2
URL:            https://github.com/mattanger/ckb-next
Source0:        https://github.com/mattanger/ckb-next/archive/master.tar.gz#/%{name}-%{version}.tar.gz

# Upstream ships third party libraries
Patch0:         0001-ckb-external-quazip.patch
# There is no qt5 of quazip in Epel
Patch1:         0002-ckb-external-quazip-epel.patch
# Workaround for color changer freeze
Patch2:         0003-ckb-color-freeze-fix.patch

# Upstream provides none of the following files
Source1:        ckb.appdata.xml
Source2:        ckb.1
Source3:        99-ckb-next.preset

BuildRequires:  qt5-qtbase-devel >= 5.2.0
%if 0%{?fedora}
BuildRequires: quazip-qt5-devel
BuildRequires:  libgudev-devel
%endif
%if 0%{?rhel}
BuildRequires:  quazip-devel
BuildRequires:  libgudev1-devel
%endif
BuildRequires:  libappindicator-devel
BuildRequires:  systemd-devel
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
%setup -q -n ckb-next-master
%if 0%{?fedora}
%patch0 -p1
%endif
%if 0%{?rhel}
%patch1 -p1
%endif
%patch2 -p1
# Correct dir for animations
sed -e 's|"/usr/lib"|"%{_libdir}"|' -i src/ckb/animscript.cpp
# Fedora uses /usr/libexec for daemons
sed -e '/^ExecStart/cExecStart=%{_libexecdir}/ckb-daemon' -i service/systemd/ckb-daemon.service

%build
qmake-qt5
make %{?_smp_mflags}

%install
install -m 644 -D etc/profile.d/ckb-next.sh %{buildroot}%{_sysconfdir}/profile.d/ckb-next.sh
install -D -m 755 bin/ckb %{buildroot}%{_bindir}/ckb
install -D -m 755 bin/ckb-daemon %{buildroot}%{_libexecdir}/ckb-daemon
install -d %{buildroot}%{_libdir}/ckb-animations
install -m 755 bin/ckb-animations/* %{buildroot}%{_libdir}/ckb-animations
install -m 644 -D usr/ckb.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/ckb.png
install -Dpm 0644 %{SOURCE3} %{buildroot}/%{_presetdir}/99-ckb-next.preset
install -m 644 -D service/systemd/ckb-daemon.service %{buildroot}%{_unitdir}/ckb-daemon.service
desktop-file-install --dir=%{buildroot}%{_datadir}/applications usr/ckb.desktop
install -Dpm 0644                                                             \
%{SOURCE1} %{buildroot}%{_datadir}/appdata/ckb.appdata.xml
appstream-util                                                                \
validate-relax --nonet %{buildroot}%{_datadir}/appdata/ckb.appdata.xml
install -Dpm 0644 %{SOURCE2} %{buildroot}%{_mandir}/man1/ckb.1

%post
%systemd_post ckb-daemon.service
if [ $1 -eq 1 ]; then
    # starting daemon also at install
    systemctl start ckb-daemon.service >/dev/null 2>&1 || :
    touch --no-create %{_datadir}/icons/hicolor >&/dev/null || :
fi

%preun
%systemd_preun ckb-daemon.service

%postun
%systemd_postun_with_restart ckb-daemon.service
if [ $1 -eq 0 ]; then
    touch --no-create %{_datadir}/icons/hicolor >&/dev/null || :
    gtk-update-icon-cache %{_datadir}/icons/hicolor >&/dev/null || :
fi

%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :


%files
%defattr(-,root,root)
%license LICENSE
%doc BUILD.md DAEMON.md FIRMWARE README.md
%{_sysconfdir}/profile.d/ckb-next.sh
%{_bindir}/ckb
%{_libexecdir}/ckb-daemon
%{_libdir}/ckb-animations
%{_unitdir}/ckb-daemon.service
%{_presetdir}/99-ckb-next.preset
%{_datadir}/applications/ckb.desktop
%{_datadir}/appdata/ckb.appdata.xml
%{_datadir}/icons/hicolor/*/apps/ckb.png
%{_mandir}/man1/ckb.1*

%changelog
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
* Thu Feb 19 2017 Johan Heikkila <johan.heikkila@gmail.com> - 0.2.7:0.6.20170219gitb59d179
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
