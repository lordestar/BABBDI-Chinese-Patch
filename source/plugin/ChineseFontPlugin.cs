using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using BepInEx;
using BepInEx.Configuration;
using BepInEx.Logging;
using TMPro;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace BabbdiChineseFont
{
    /// <summary>
    /// BABBDI 中文字体支持插件。
    ///
    /// 【为什么需要这个插件】
    /// BABBDI 是 Unity 2022.1.5f1 (Mono) 构建，界面用 TextMeshPro，
    /// 字体是 LiberationSans SDF / monofonto rg SDF / FuturaHandwritten SDF，
    /// 这些字体图集只有拉丁字形、不含汉字，所以直接汉化会显示成方块（豆腐块）。
    /// XUnity.AutoTranslator 自带的字体覆盖功能要求 TMP 3.2.0+，
    /// 而本作只有 TMP 1.x/3.0 的 API，因此必须由本插件补上字体。
    ///
    /// 【实现要点】
    /// 关键在 <c>new Font(字体文件完整路径)</c>：
    /// UnityEngine.Font 的单参数构造函数会判断参数里有没有目录，
    /// 有目录时走 Internal_CreateFontFromPath —— 把真正的字体文件交给
    /// 底层 FontEngine，这样 TMP_FontAsset.CreateFontAsset 才能成功，
    /// 而且后续动态扩充字形图集（TryAddCharacters）也能正常工作。
    ///
    /// 反面教材：Font.CreateDynamicFontFromOSFont("SimHei", 90) 虽然能拿到
    /// Font 对象，但它没有字体文件路径，FontEngine.LoadFontFace 会失败，
    /// TMP_FontAsset.CreateFontAsset 直接返回 null（实测所有系统字体皆如此）。
    ///
    /// 最后把创建好的中文字体注册为游戏所有 TMP 字体资源的「回退字体」：
    /// 英文/数字继续用游戏原字体，汉字自动由中文字体补齐。
    /// </summary>
    [BepInPlugin(Guid, "BABBDI 中文字体支持", "1.1.0")]
    public class ChineseFontPlugin : BaseUnityPlugin
    {
        public const string Guid = "babbdi.chinesefont";

        internal static ManualLogSource Log;

        /// <summary>候选字体文件（按优先级）：Windows 自带的中文字体。</summary>
        private static readonly string[] PreferredFontFiles =
        {
            "Deng.ttf",      // 等线：现代干净，最贴合本作气质
            "simhei.ttf",    // 黑体
            "msyh.ttc",      // 微软雅黑
            "Dengb.ttf",     // 等线 Bold
            "simkai.ttf",    // 楷体
            "simfang.ttf",   // 仿宋
            "msyhbd.ttc",
            "simsun.ttc",    // 宋体
            "msjh.ttc",      // 微软正黑体
            "msyhl.ttc"
        };

        /// <summary>扫描字体目录时用于识别中文字体的文件名关键字。</summary>
        private static readonly string[] FileKeywords =
        {
            "deng", "simhei", "simsun", "simkai", "simfang", "msyh", "msjh",
            "noto", "sourcehan", "source-han", "harmony", "misans", "alibaba",
            "wenquanyi", "hei", "song", "kai", "ming", "gothic", "cjk"
        };

        /// <summary>用于验证字体是否真的能渲染汉字的测试串。</summary>
        private const string ProbeText = "汉字测试中文";

        private ConfigEntry<bool> _overrideAllFonts;
        private ConfigEntry<string> _forcedFontFile;
        private ConfigEntry<bool> _verbose;
        private ConfigEntry<bool> _dumpTexts;
        private ConfigEntry<bool> _translateLeftovers;

        private TMP_FontAsset _cjkFont;
        private bool _resolved;
        private bool _givenUp;
        private int _rounds;
        private float _nextAttempt;
        private float _nextRescan;
        private float _nextDump;
        private float _nextComplete;
        private float _nextAudit;

        private readonly Dictionary<int, string> _lastSeenTexts = new Dictionary<int, string>();

        /// <summary>汉化词典：英文原文 -> 简体中文。用于"补漏层"。</summary>
        private readonly Dictionary<string, string> _dict =
            new Dictionary<string, string>(StringComparer.Ordinal);

        private void Awake()
        {
            Log = Logger;
            _overrideAllFonts = Config.Bind(
                "General", "OverrideAllFonts", false,
                "true = 把游戏里所有文本都强制换成中文字体；false = 只作为缺字回退字体（推荐，保留游戏原有英文字体风格）");
            _forcedFontFile = Config.Bind(
                "General", "FontFile", "",
                @"手动指定中文字体文件完整路径（.ttf/.otf/.ttc），例如 C:\Windows\Fonts\Deng.ttf，留空为自动选择");
            _verbose = Config.Bind(
                "General", "VerboseLogging", true,
                "输出详细的调试日志");
            _dumpTexts = Config.Bind(
                "General", "DumpGameTexts", false,
                "调试用：把游戏运行时的所有文本写入日志，用于核对汉化词典");
            _translateLeftovers = Config.Bind(
                "General", "TranslateLeftovers", true,
                "补漏层：自动翻译那些在插件挂钩之前就已写入、XUnity 没抓到的文本（如选项面板标签）");

            Log.LogInfo("[BABBDI-CN] 中文字体插件已加载，等待 TMP 初始化…");
        }

        private void OnEnable() { SceneManager.sceneLoaded += OnSceneLoaded; }
        private void OnDisable() { SceneManager.sceneLoaded -= OnSceneLoaded; }
        private void OnSceneLoaded(Scene scene, LoadSceneMode mode) { _nextRescan = 0f; }

        private void Update()
        {
            if (!_resolved && !_givenUp)
            {
                if (Time.unscaledTime < _nextAttempt) return;
                _nextAttempt = Time.unscaledTime + 1f;
                _rounds++;

                try
                {
                    TryCreateFontAsset();
                }
                catch (Exception e)
                {
                    Log.LogError("[BABBDI-CN] 创建中文字体时出错：" + e);
                }

                if (!_resolved && _rounds >= 5)
                {
                    _givenUp = true;
                    Log.LogError("[BABBDI-CN] 尝试 " + _rounds + " 轮后仍无法创建中文字体。");
                    Log.LogError("[BABBDI-CN] 请编辑 BepInEx\\config\\babbdi.chinesefont.cfg，");
                    Log.LogError("[BABBDI-CN] 把 FontFile 设为一个中文字体文件的完整路径后重启游戏。");
                }
                return;
            }

            // 定期把回退字体挂到新出现的 TMP 字体资源上（对话场景的字体是后加载的）
            if (_resolved && Time.unscaledTime >= _nextRescan)
            {
                _nextRescan = Time.unscaledTime + 5f;
                try
                {
                    AttachToGameFontAssets();
                    if (_overrideAllFonts.Value) ApplyOverrideToAllTexts();
                }
                catch (Exception e)
                {
                    Log.LogWarning("[BABBDI-CN] 重新挂载字体时出错：" + e.Message);
                }
            }

            // 调试：转储游戏运行时真实文本
            if (_resolved && _dumpTexts.Value && Time.unscaledTime >= _nextDump)
            {
                _nextDump = Time.unscaledTime + 0.5f;
                DumpTexts();
            }

            // 调试：每 10 秒做一次字形审计，报出仍有缺字（会显示成方框）的文本
            if (_resolved && _dumpTexts.Value && Time.unscaledTime >= _nextAudit)
            {
                _nextAudit = Time.unscaledTime + 10f;
                AuditGlyphs();
            }

            // 补漏层：翻译 XUnity 漏掉的文本
            if (_resolved && _translateLeftovers.Value && Time.unscaledTime >= _nextComplete)
            {
                _nextComplete = Time.unscaledTime + 0.5f;
                try
                {
                    CompleteTranslations();
                }
                catch (Exception e)
                {
                    Log.LogWarning("[BABBDI-CN] 补漏层出错：" + e.Message);
                }
            }
        }

        // ==================================================================

        private void TryCreateFontAsset()
        {
            if (TMP_Settings.instance == null)
            {
                if (_verbose.Value) Log.LogInfo("[BABBDI-CN] TMP 尚未初始化，稍后重试…");
                return;
            }

            List<string> candidates = BuildCandidateFiles();
            if (candidates.Count == 0)
            {
                Log.LogError("[BABBDI-CN] 未找到任何候选中文字体文件。");
                return;
            }

            if (_verbose.Value)
            {
                Log.LogInfo("[BABBDI-CN] 本轮尝试 " + candidates.Count + " 个字体文件："
                    + string.Join(" / ", candidates.Select(Path.GetFileName).ToArray()));
            }

            foreach (string path in candidates)
            {
                TMP_FontAsset asset = CreateFromFontFile(path);
                if (asset == null) continue;

                string missing;
                bool ok;
                try
                {
                    ok = asset.TryAddCharacters(ProbeText, out missing, true);
                }
                catch (Exception e)
                {
                    Log.LogWarning("[BABBDI-CN] " + Path.GetFileName(path) + " 字形写入异常：" + e.Message);
                    continue;
                }

                if (!ok || !string.IsNullOrEmpty(missing))
                {
                    Log.LogWarning("[BABBDI-CN] " + Path.GetFileName(path)
                        + " 缺少汉字字形，跳过（缺失：" + (missing ?? "?") + "）");
                    continue;
                }

                _cjkFont = asset;
                _resolved = true;
                Log.LogInfo("[BABBDI-CN] ★ 中文字体创建成功：" + Path.GetFileName(path));
                Log.LogInfo("[BABBDI-CN]   资源名=" + asset.name
                    + " | TMP字体版本=" + asset.version
                    + " | 图集模式=" + asset.atlasPopulationMode);

                WarmUp();
                AttachToGameFontAssets();
                LoadDictionary();
                if (_overrideAllFonts.Value) ApplyOverrideToAllTexts();
                return;
            }

            Log.LogWarning("[BABBDI-CN] 第 " + _rounds + " 轮：所有候选字体均创建失败，1 秒后重试。");
        }

        /// <summary>
        /// 从字体文件创建 TMP 动态字体资源；失败返回 null。
        /// 核心：new Font(完整路径) -> Internal_CreateFontFromPath -> FontEngine 能读到字体文件。
        /// </summary>
        private TMP_FontAsset CreateFromFontFile(string path)
        {
            try
            {
                if (!File.Exists(path))
                {
                    if (_verbose.Value) Log.LogInfo("[BABBDI-CN]   × 文件不存在：" + path);
                    return null;
                }

                var font = new Font(path);   // 关键：带目录路径 -> Internal_CreateFontFromPath
                if (font == null)
                {
                    if (_verbose.Value) Log.LogInfo("[BABBDI-CN]   × new Font 返回 null：" + Path.GetFileName(path));
                    return null;
                }

                TMP_FontAsset asset = TMP_FontAsset.CreateFontAsset(font);
                if (asset == null)
                {
                    if (_verbose.Value) Log.LogInfo("[BABBDI-CN]   × CreateFontAsset 返回 null：" + Path.GetFileName(path));
                    return null;
                }

                asset.name = "BABBDI CJK (" + Path.GetFileNameWithoutExtension(path) + ")";
                asset.atlasPopulationMode = AtlasPopulationMode.Dynamic;
                asset.isMultiAtlasTexturesEnabled = true;

                GameObject.DontDestroyOnLoad(font);
                GameObject.DontDestroyOnLoad(asset);
                return asset;
            }
            catch (Exception e)
            {
                if (_verbose.Value) Log.LogInfo("[BABBDI-CN]   × " + Path.GetFileName(path) + "：" + e.Message);
                return null;
            }
        }

        /// <summary>构造候选字体文件列表（完整路径）。</summary>
        private List<string> BuildCandidateFiles()
        {
            var result = new List<string>();

            if (!string.IsNullOrEmpty(_forcedFontFile.Value))
            {
                string p = _forcedFontFile.Value.Trim().Trim('"');
                if (File.Exists(p)) result.Add(p);
                else Log.LogError("[BABBDI-CN] 配置指定的字体文件不存在：" + p);
                return result;
            }

            // 0) 插件自己所在目录里的字体文件
            //    用户只要把任意中文字体（.ttf/.otf/.ttc）丢进本插件目录即可强制使用它，
            //    这对没有中文系统字体的 Windows 环境很有用。
            try
            {
                string selfDir = Path.GetDirectoryName(Info.Location);
                if (!string.IsNullOrEmpty(selfDir) && Directory.Exists(selfDir))
                {
                    var own = Directory.GetFiles(selfDir, "*.ttf")
                        .Concat(Directory.GetFiles(selfDir, "*.otf"))
                        .Concat(Directory.GetFiles(selfDir, "*.ttc"));
                    foreach (string f in own)
                    {
                        if (!result.Contains(f)) result.Add(f);
                    }
                    if (result.Count > 0)
                    {
                        Log.LogInfo("[BABBDI-CN] 在插件目录发现自带字体文件，优先使用。");
                    }
                }
            }
            catch (Exception e)
            {
                Log.LogWarning("[BABBDI-CN] 扫描插件目录字体失败：" + e.Message);
            }

            foreach (string dir in GetFontDirectories())
            {
                if (string.IsNullOrEmpty(dir) || !Directory.Exists(dir)) continue;

                // 1) 优先按已知文件名匹配
                foreach (string name in PreferredFontFiles)
                {
                    string full = Path.Combine(dir, name);
                    if (File.Exists(full) && !result.Contains(full)) result.Add(full);
                }

                // 2) 再按关键字扫描目录
                try
                {
                    var files = Directory.GetFiles(dir, "*.tt*")
                        .Concat(Directory.GetFiles(dir, "*.otf"))
                        .Concat(Directory.GetFiles(dir, "*.otc"));

                    foreach (string f in files)
                    {
                        string low = Path.GetFileName(f).ToLowerInvariant();
                        if (FileKeywords.Any(k => low.Contains(k)) && !result.Contains(f))
                        {
                            result.Add(f);
                        }
                    }
                }
                catch (Exception e)
                {
                    Log.LogWarning("[BABBDI-CN] 扫描字体目录失败 " + dir + "：" + e.Message);
                }
            }

            if (result.Count > 12) result = result.GetRange(0, 12);
            return result;
        }

        private static IEnumerable<string> GetFontDirectories()
        {
            yield return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Windows), "Fonts");
            yield return Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                @"Microsoft\Windows\Fonts");
        }

        private void WarmUp()
        {
            string charset = LoadCharset();
            if (string.IsNullOrEmpty(charset)) return;

            try
            {
                string missing;
                bool ok = _cjkFont.TryAddCharacters(charset, out missing, true);
                Log.LogInfo("[BABBDI-CN] 字形预热：字符数=" + charset.Length
                    + " 全部成功=" + ok
                    + " 缺失=" + (string.IsNullOrEmpty(missing) ? "无" : missing));
            }
            catch (Exception e)
            {
                Log.LogWarning("[BABBDI-CN] 字形预热失败（不影响使用）：" + e.Message);
            }
        }

        private string LoadCharset()
        {
            try
            {
                string dir = Path.GetDirectoryName(Info.Location);
                if (!string.IsNullOrEmpty(dir))
                {
                    string path = Path.Combine(dir, "charset.txt");
                    if (File.Exists(path))
                    {
                        string text = File.ReadAllText(path, Encoding.UTF8);
                        var set = new HashSet<char>();
                        foreach (char c in text)
                        {
                            // 汉字、全角标点、中文引号、省略号……凡是译文里用到的非 ASCII 字符都要预热
                            if (c >= 0x20 && c != 0x7F && !char.IsWhiteSpace(c)) set.Add(c);
                        }
                        if (set.Count > 0) return new string(set.ToArray());
                    }
                }
            }
            catch (Exception e)
            {
                Log.LogWarning("[BABBDI-CN] 读取 charset.txt 失败：" + e.Message);
            }
            return ProbeText;
        }

        // ==================================================================

        private void AttachToGameFontAssets()
        {
            if (_cjkFont == null) return;

            int attached = 0;

            // 1) TMP 全局回退字体列表
            try
            {
                List<TMP_FontAsset> global = TMP_Settings.fallbackFontAssets;
                if (global != null && !global.Contains(_cjkFont))
                {
                    global.Add(_cjkFont);
                    attached++;
                }
            }
            catch (Exception e)
            {
                Log.LogWarning("[BABBDI-CN] 无法写入 TMP 全局回退列表：" + e.Message);
            }

            // 2) 每个游戏字体资源自己的回退表（这条路径最可靠）
            TMP_FontAsset[] all = Resources.FindObjectsOfTypeAll<TMP_FontAsset>();
            foreach (TMP_FontAsset fa in all)
            {
                if (fa == null || fa == _cjkFont) continue;

                if (fa.fallbackFontAssetTable == null)
                {
                    fa.fallbackFontAssetTable = new List<TMP_FontAsset>();
                }
                if (!fa.fallbackFontAssetTable.Contains(_cjkFont))
                {
                    fa.fallbackFontAssetTable.Add(_cjkFont);
                    attached++;
                    if (_verbose.Value) Log.LogInfo("[BABBDI-CN] 已为字体挂上中文回退：" + fa.name);
                }
            }

            if (attached > 0) Log.LogInfo("[BABBDI-CN] 本次挂载回退字体 " + attached + " 处。");
        }

        private void ApplyOverrideToAllTexts()
        {
            if (_cjkFont == null) return;

            TMP_Text[] texts = Resources.FindObjectsOfTypeAll<TMP_Text>();
            int changed = 0;
            foreach (TMP_Text t in texts)
            {
                if (t == null) continue;
                if (t.font != _cjkFont)
                {
                    t.font = _cjkFont;
                    changed++;
                }
            }
            if (changed > 0 && _verbose.Value)
            {
                Log.LogInfo("[BABBDI-CN] 已强制替换 " + changed + " 个文本对象的字体。");
            }
        }

        // ==================================================================
        //  补漏层
        //
        //  XUnity.AutoTranslator 是"挂钩式"翻译：只有经过 TMP_Text.text 赋值
        //  的文本才会被它翻译。而本作有不少标签是在场景加载时就序列化好的
        //  （例如选项面板里的 ULTRA / CONTROLS / SOUND EFFECT），早于插件挂钩，
        //  于是就漏掉了。这里主动扫描全部 TMP 文本组件（包括未激活的对象），
        //  凡是内容与词典完全一致、且尚未变成中文的，直接替换掉。
        // ==================================================================

        private void LoadDictionary()
        {
            if (_dict.Count > 0) return;

            string gameRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            var dirs = new[]
            {
                Path.Combine(gameRoot, "BepInEx", "Translation", "zh-CN", "Text"),
                Path.Combine(gameRoot, "Translation", "zh-CN", "Text")
            };

            int files = 0, lines = 0;
            foreach (string dir in dirs)
            {
                if (!Directory.Exists(dir)) continue;

                foreach (string file in Directory.GetFiles(dir, "*.txt"))
                {
                    if (Path.GetFileName(file).StartsWith("_")) continue;   // 跳过自动生成的文件

                    foreach (string raw in File.ReadAllLines(file, Encoding.UTF8))
                    {
                        string line = raw.TrimEnd('\r', '\n');
                        if (line.Length == 0 || line[0] == '#' || line[0] == ';') continue;
                        if (line.StartsWith("r:") || line.StartsWith("sr:")) continue;  // 正则条目交给 XUnity

                        int idx = line.IndexOf('=');
                        if (idx <= 0) continue;

                        string key = line.Substring(0, idx);
                        string val = line.Substring(idx + 1);
                        if (key.Length == 0 || val.Length == 0) continue;

                        _dict[key] = val;
                        lines++;

                        string trimmedKey = key.Trim();
                        if (trimmedKey.Length > 0 && !_dict.ContainsKey(trimmedKey))
                        {
                            _dict[trimmedKey] = val;   // 便于匹配带首尾空白的原文
                        }
                    }
                    files++;
                }
            }

            Log.LogInfo("[BABBDI-CN] 补漏层已载入词典：" + _dict.Count + " 条（" + files + " 个文件 / " + lines + " 行）");
        }

        private void CompleteTranslations()
        {
            if (_dict.Count == 0) LoadDictionary();
            if (_dict.Count == 0) return;

            TMP_Text[] texts = Resources.FindObjectsOfTypeAll<TMP_Text>();
            int fixedCount = 0;

            foreach (TMP_Text t in texts)
            {
                if (t == null) continue;

                string cur;
                try { cur = t.text; }
                catch { continue; }
                if (string.IsNullOrEmpty(cur)) continue;
                if (HasCjk(cur)) continue;                 // 已经是中文，跳过

                string zh;
                if (_dict.TryGetValue(cur, out zh))
                {
                    try { t.text = zh; fixedCount++; }
                    catch { }
                    continue;
                }

                // 带首尾空白（如 "BACK\n"、"MUSIC "）的情况：保留空白，只换中间
                string trimmed = cur.Trim();
                if (trimmed.Length == 0 || trimmed.Length == cur.Length) continue;

                if (_dict.TryGetValue(trimmed, out zh))
                {
                    int at = cur.IndexOf(trimmed, StringComparison.Ordinal);
                    if (at < 0) continue;
                    try
                    {
                        t.text = cur.Substring(0, at) + zh + cur.Substring(at + trimmed.Length);
                        fixedCount++;
                    }
                    catch { }
                }
            }

            if (fixedCount > 0 && _verbose.Value)
            {
                Log.LogInfo("[BABBDI-CN] 补漏层：本次补翻 " + fixedCount + " 条文本。");
            }
        }

        private static bool HasCjk(string s)        {
            for (int i = 0; i < s.Length; i++)
            {
                if (s[i] >= 0x4E00 && s[i] <= 0x9FFF) return true;
            }
            return false;
        }

        // ==================================================================

        /// <summary>调试用：统计仍有缺字的文本（缺字会显示成方框）。</summary>
        private void AuditGlyphs()
        {
            TMP_Text[] texts = Resources.FindObjectsOfTypeAll<TMP_Text>();
            int total = 0, bad = 0;
            var samples = new List<string>();

            foreach (TMP_Text t in texts)
            {
                if (t == null) continue;
                string cur;
                try { cur = t.text; }
                catch { continue; }
                if (string.IsNullOrEmpty(cur)) continue;
                total++;

                int missing = 0;
                var mc = new StringBuilder();
                foreach (char c in cur)
                {
                    if (c == '\n' || c == '\r' || c == ' ' || c == '\t') continue;
                    bool ok = false;
                    try
                    {
                        if ((t.font != null && t.font.HasCharacter(c))
                            || (_cjkFont != null && _cjkFont.HasCharacter(c))) ok = true;
                    }
                    catch { ok = true; }

                    if (!ok)
                    {
                        missing++;
                        if (mc.Length < 10) mc.Append(c);
                    }
                }

                if (missing > 0)
                {
                    bad++;
                    if (samples.Count < 6)
                    {
                        string go = t.gameObject != null ? t.gameObject.name : "?";
                        samples.Add(go + "=[" + mc + "]");
                    }
                }
            }

            Log.LogInfo("[BABBDI-CN] 字形审计：文本组件=" + total
                + " 有缺字的=" + bad
                + (bad > 0 ? " | 样例：" + string.Join("; ", samples.ToArray()) : " | 全部字符均可正常渲染"));
        }

        /// <summary>调试用：把游戏运行时真实出现的文本写入日志。</summary>
        private void DumpTexts()
        {
            TMP_Text[] texts = Resources.FindObjectsOfTypeAll<TMP_Text>();
            foreach (TMP_Text t in texts)
            {
                if (t == null) continue;

                string current;
                try { current = t.text; }
                catch { continue; }
                if (current == null) continue;

                int id = t.GetInstanceID();
                string previous;
                if (_lastSeenTexts.TryGetValue(id, out previous) && previous == current) continue;
                _lastSeenTexts[id] = current;

                string go = "<null>";
                try { if (t.gameObject != null) go = t.gameObject.name; }
                catch { }

                // 字形覆盖校验：确认这段文本的每个字都能渲染出来（否则会显示成方框）
                int missing = 0;
                var missingChars = new StringBuilder();
                foreach (char c in current)
                {
                    if (c == '\n' || c == '\r' || c == ' ' || c == '\t') continue;
                    bool ok = false;
                    try
                    {
                        if (t.font != null && t.font.HasCharacter(c)) ok = true;
                        else if (_cjkFont != null && _cjkFont.HasCharacter(c)) ok = true;
                    }
                    catch { ok = true; }

                    if (!ok)
                    {
                        missing++;
                        if (missingChars.Length < 20) missingChars.Append(c);
                    }
                }

                Log.LogInfo("[TEXT] obj=\"" + go + "\" font=\"" + (t.font != null ? t.font.name : "null")
                    + "\" len=" + current.Length
                    + " 缺字=" + missing + (missing > 0 ? " [" + missingChars + "]" : "")
                    + " 字号=" + t.fontSize
                    + " 框宽=" + (t.rectTransform != null ? (int)t.rectTransform.rect.width : -1)
                    + " 换行=" + t.enableWordWrapping
                    + " 需要宽=" + (int)t.preferredWidth
                    + " text=[" + current.Replace("\n", "\\n") + "]");
            }
        }
    }
}
