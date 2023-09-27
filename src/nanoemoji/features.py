# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Helps deal with emoji OpenType Layout features."""

# TODO if this is a qualified sequence create the unqualified version and vice versa


from nanoemoji.glyph import glyph_name


DEFAULT_GSUB_FEATURE_TAG = "ccmp"


def generate_fea(rgi_sequences, feature_tag=DEFAULT_GSUB_FEATURE_TAG, feature_file=None):
    begin_text = ""
    end_text = ""
    if feature_file:
        with open(feature_file, "r") as f:
            lines = f.readlines()
            in_begin_section = False

            for line in lines:
                if line.strip() == ">>>> Begin":
                    in_begin_section = True
                elif line.strip() == ">>>> End":
                    in_begin_section = False
                elif in_begin_section:  
                    begin_text += line
                else:
                    end_text += line 

    # Generate feature with ligature lookup for multi-codepoint RGIs
    rules = []
    dflt_string = "languagesystem DFLT dflt;"
    latn_string = "languagesystem latn dflt;"
    if dflt_string not in begin_text:
        rules.append(dflt_string)
    if latn_string not in begin_text:
        rules.append(latn_string)
    if begin_text:
        rules.append(begin_text)
    rules.append("")

    rules.append(f"feature {feature_tag} {{")
    for rgi in sorted(rgi_sequences):
        if len(rgi) == 1:
            continue
        glyphs = [glyph_name(cp) for cp in rgi]
        target = glyph_name(rgi)
        rules.append("  sub %s by %s;" % (" ".join(glyphs), target))

    if end_text:
        rules.append(end_text)
    
    if (f"}} {feature_tag};") not in rules:
        rules.append(f"}} {feature_tag};")

    rules.append("")
    return "\n".join(rules)
