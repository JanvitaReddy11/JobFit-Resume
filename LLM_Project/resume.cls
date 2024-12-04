\ProvidesClass{resume}[2024/11/19 Resume class]
\LoadClass[10pt]{article} % Base class is article

% Adjust margins for a resume
\setlength{\textwidth}{7.5in}        % Width of the content area
\setlength{\textheight}{9in}         % Height of the content area
\setlength{\oddsidemargin}{-0.5in}   % Decrease left margin
\setlength{\evensidemargin}{-0.5in}  % Same for even pages (if needed)
\setlength{\topmargin}{-0.90in}      % Top margin adjustment


% Remove paragraph indentation and add space between paragraphs
\usepackage[parfill]{parskip}
\usepackage[hidelinks]{hyperref} 
% Disable page numbering
\pagestyle{empty}

% Custom commands
\newcommand{\name}[1]{\centerline{\LARGE \textbf{#1}}}
\newcommand{\details}[4]{%
  \centerline{#1 $|$ \href{#2}{#2} $|$ \href{#3}{#3} $|$ \href{#4}{#4}}
}


\newenvironment{rSection}[1]{%
  \noindent\textbf{\large \MakeUppercase{#1}}\par\vspace{3pt}\hrule
}

%------------Education Section-----------------------%
\usepackage{enumitem} 
\newenvironment{rSubsectionedu}[6]{%
\begin{itemize}[left=-5pt,align=parleft, label={}]  
\item[] \textbf{#1}, #2 \hfill \textit{#3} \\ 
{#4}, {#5},\textit{CGPA: #6} \\  
\end{itemize}}

%-------------------Work Section--------------------%
\newenvironment{rSubsectionWork}[4]{%
  \textbf{#1} | \textbf{#2}, {#3} \hfill \textit{#4} \\ % Title and timeline
  \vspace{-15pt} 
  \begin{itemize}[label=\scriptsize$\bullet$, left=5pt, itemsep=-3pt] 
}{%
  \end{itemize}}
%------------------------------------------------------%
%-------------------Project Section--------------------%
\newenvironment{rSubsectionProj}[1]{%
  \textbf{#1}  \\ % Title and timeline
  \vspace{-15pt} % Space between title and list
  \begin{itemize}[label=\scriptsize$\bullet$, left=5pt, itemsep=-3pt] % Bullet list with spacing
}{%
  \end{itemize}}

%-------------------------------------------------------%


