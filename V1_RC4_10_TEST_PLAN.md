# V1.0.0 RC4.10 Android libffi 修复测试

## 完整日志中的真实根因

RC4.9 已经正确使用：

```text
hostpython3 3.11.15
python3     3.11.15
PySide6     6.11.1
p4a         v2026.05.09
```

真正失败发生在：

```text
Building libffi for arm64-v8a
-> running autogen.sh
```

随后：

```text
configure.ac:215: error:
possibly undefined macro: LT_SYS_SYMBOL_USCORE

autoreconf: error:
/usr/bin/autoconf failed with exit status: 1
```

因此问题是 Linux Runner 的 autotools/libltdl 构建前置依赖，
不是应用 Python 代码，也不是 PySide6 wheel ABI。

## RC4.10 修复

Runner 固定：

```text
ubuntu-24.04
```

Android CI 显式安装：

```text
autoconf
automake
autopoint
cmake
gettext
libffi-dev
libltdl-dev
libncurses5-dev
libncursesw5-dev
libssl-dev
libtinfo6
libtool
libtool-bin
m4
pkg-config
zlib1g-dev
zip
unzip
```

并在构建前检查：

```text
/usr/share/aclocal/ltdl.m4
LT_SYS_SYMBOL_USCORE
```

预期出现：

```text
Install Android native build prerequisites
✓

libltdl autoconf macro verification: OK
```

之后 `Building libffi for arm64-v8a` 不应再因为
`LT_SYS_SYMBOL_USCORE` 失败。

## 成功目标

```text
Build Android APK Beta
✓
Validate collected APK/AAB
✓
Upload Android Beta
✓
```

下载：

```text
StockEventRadar-Android-Beta-1.0.0-rc4.10
```

如果出现下一处 native build 错误，继续使用
`android-deploy.log` 定位第一处真实错误即可。
